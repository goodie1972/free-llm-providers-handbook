# -*- coding: utf-8 -*-
"""校验 markdown 里的相对链接是否指向真实文件。

用法：
    python check_md_links.py <仓库根目录>

为什么需要它：
    手写 README / invites.md 的相对路径极易出错，而且**在本地看不出来**。
    典型错法：文件在 data/ 目录下，却写 `articles/xxx.md` —— 本地目录遍历碰巧能找到
    同名文件时不会报错，但 GitHub 上按 blob 路径解析会 404。
    正确写法是 `../articles/xxx.md`。

注意（已知误报，不用改）：
    README 里指向 issue 列表的 `../../issues` 会被本脚本判为断链，
    但 GitHub 按 blob 路径解析其实是对的（/owner/repo/blob/main/ 的两位上级 = /owner/repo/）。
    本脚本已默认跳过含 'issues' 的链接。
"""
import os
import re
import sys
import urllib.parse

SKIP_MARKERS = ('issues', 'pulls', 'releases')


def check(root):
    bad, ok = [], 0
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d != '.git']
        for fn in filenames:
            if not fn.endswith('.md'):
                continue
            full = os.path.join(dirpath, fn)
            rel_md = os.path.relpath(full, root).replace(os.sep, '/')
            txt = open(full, encoding='utf-8').read()
            for m in re.finditer(r'\]\(([^)]+)\)', txt):
                link = m.group(1).strip()
                if link.startswith(('http', 'mailto:', '#')):
                    continue
                if any(s in link for s in SKIP_MARKERS):
                    continue
                target = link.split('#')[0]
                if not target:
                    continue
                path = os.path.normpath(
                    os.path.join(os.path.dirname(full), urllib.parse.unquote(target)))
                if os.path.exists(path):
                    ok += 1
                else:
                    bad.append((rel_md, link, os.path.relpath(path, root)))

    print('✅ 可解析的相对链接: %d' % ok)
    print('❌ 断链: %d' % len(bad))
    for b in bad:
        print('   %-28s -> %-46s (解析为 %s)' % b)
    return 1 if bad else 0


if __name__ == '__main__':
    root = sys.argv[1] if len(sys.argv) > 1 else '.'
    sys.exit(check(root))
