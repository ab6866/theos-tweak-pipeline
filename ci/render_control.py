#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
按 package scheme 渲染 control。

命名规范（固定）：
  Name        应用名称 + " OK"
  Package     应用 bundle id（两个 scheme 相同，靠 Architecture 区分）
  Description 解锁该应用的全部功能。
  Author      6866

两个 scheme 的 Package ID 相同，但：
  · Architecture 不同 —— RootHide = iphoneos-arm64e，Rootless = iphoneos-arm64
    （由 Theos 按 scheme 自动设置，这里不写）
  · 各自显式 Conflicts/Replaces 指向对方，确保不可共装

用法： SCHEME=roothide python3 ci/render_control.py
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def main():
    scheme = os.environ.get('SCHEME', '').strip()
    if scheme not in ('roothide', 'rootless'):
        print('!! SCHEME 必须是 roothide 或 rootless', file=sys.stderr)
        return 1

    # Package ID = 应用 bundle id（由 PKG_ID 提供）
    pkg_id = os.environ.get('PKG_ID', '').strip()
    if not pkg_id:
        print('!! 需要 PKG_ID（应用 bundle id）', file=sys.stderr)
        return 1

    # 包名 = 应用名称 + " OK"
    app_name = os.environ.get('PKG_APP_NAME', '').strip()
    if not app_name:
        print('!! 需要 PKG_APP_NAME（应用显示名称）', file=sys.stderr)
        return 1

    src = open(os.path.join(ROOT, 'control.in'), encoding='utf-8').read()

    # 两个 scheme 用同一个 Package ID，靠 Architecture 区分；
    # Conflicts/Replaces 也指向自己 —— 让 dpkg 只保留一个架构版本。
    subs = {
        '@@PKG_ID@@': pkg_id,
        '@@PKG_NAME@@': '%s OK' % app_name,
        '@@PKG_VERSION@@': os.environ.get('PKG_VERSION', ''),
        '@@PKG_AUTHOR@@': os.environ.get('PKG_AUTHOR', '6866'),
        '@@PKG_DESC@@': os.environ.get('PKG_DESC', '解锁该应用的全部功能。'),
        '@@PKG_CONFLICT@@': pkg_id,
    }
    for k, v in subs.items():
        src = src.replace(k, v)

    # Architecture 交给 Theos 按 scheme 决定
    src = '\n'.join(l for l in src.split('\n') if not l.startswith('Architecture:'))

    leftover = src.count('@@')
    if leftover:
        print('!! control 仍有 %d 处未替换占位符' % leftover, file=sys.stderr)
        return 1

    open(os.path.join(ROOT, 'control'), 'w', encoding='utf-8').write(src)
    print('control 已渲染: scheme=%s' % scheme)
    print('---')
    print(src)


if __name__ == '__main__':
    sys.exit(main())
