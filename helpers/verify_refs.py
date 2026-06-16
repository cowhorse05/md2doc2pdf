#!/usr/bin/env python3
"""
参考文献验证器 — 验证 DOI 和论文标题是否真实存在。
纯 Python stdlib，零依赖。

用法:
  python3 helpers/verify_refs.py references.bib          # 验证 .bib 文件
  python3 helpers/verify_refs.py --doi 10.1000/xyz       # 验证单个 DOI
  python3 helpers/verify_refs.py --title "Deep Learning"  # 搜索论文标题
"""

import argparse
import json
import re
import sys
import urllib.request
from pathlib import Path
from typing import Optional


def verify_doi(doi: str) -> Optional[dict]:
    """通过 CrossRef API 验证 DOI。返回论文元数据，失败返回 None。"""
    url = f'https://api.crossref.org/works/{doi}'
    req = urllib.request.Request(url, headers={'User-Agent': 'DocWizard/3.0'})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())
            if data.get('status') == 'ok':
                msg = data['message']
                return {
                    'title': msg.get('title', ['?'])[0],
                    'doi': msg.get('DOI', doi),
                    'type': msg.get('type', '?'),
                    'year': msg.get('published-print', {}).get('date-parts', [[0]])[0][0],
                }
    except Exception:
        pass
    return None


def search_semantic_scholar(title: str) -> Optional[dict]:
    """通过 Semantic Scholar API 搜索论文标题。"""
    query = urllib.parse.quote(title)
    url = f'https://api.semanticscholar.org/graph/v1/paper/search?query={query}&limit=1'
    req = urllib.request.Request(url, headers={'User-Agent': 'DocWizard/3.0'})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())
            papers = data.get('data', [])
            if papers:
                p = papers[0]
                return {
                    'title': p.get('title', '?'),
                    'paperId': p.get('paperId'),
                    'year': p.get('year'),
                    'authors': [a.get('name') for a in p.get('authors', [])],
                }
    except Exception:
        pass
    return None


def parse_bibtex_dois(path: Path) -> list:
    """从 .bib 文件中提取所有 DOI。"""
    content = path.read_text(encoding='utf-8', errors='replace')
    dois = re.findall(r'doi\s*=\s*[{"](.+?)[}"]', content, re.IGNORECASE)
    return dois


def verify_bibtex(path: Path) -> dict:
    """验证 .bib 文件中的所有参考文献。"""
    dois = parse_bibtex_dois(path)
    results = {'total': len(dois), 'verified': 0, 'failed': 0, 'details': []}

    for doi in dois:
        meta = verify_doi(doi)
        if meta:
            results['verified'] += 1
            results['details'].append({'doi': doi, 'status': 'OK', 'meta': meta})
            print(f"  ✅ {doi} → {meta['title'][:60]}...")
        else:
            results['failed'] += 1
            results['details'].append({'doi': doi, 'status': 'FAIL'})
            print(f"  ❌ {doi} → 未找到")

    return results


def main():
    parser = argparse.ArgumentParser(description='DocWizard 参考文献验证器')
    parser.add_argument('input', nargs='?', help='.bib 文件路径')
    parser.add_argument('--doi', help='验证单个 DOI')
    parser.add_argument('--title', help='通过 Semantic Scholar 搜索论文标题')
    args = parser.parse_args()

    if args.doi:
        print(f"验证 DOI: {args.doi}")
        meta = verify_doi(args.doi)
        if meta:
            print(f"  ✅ 存在: {meta['title']} ({meta['year']})")
        else:
            print(f"  ❌ 未找到此 DOI")
        sys.exit(0 if meta else 1)

    if args.title:
        print(f"搜索论文: {args.title}")
        meta = search_semantic_scholar(args.title)
        if meta:
            print(f"  ✅ 找到: {meta['title']} ({meta['year']})")
            print(f"     作者: {', '.join(meta['authors'][:3])}")
        else:
            print(f"  ❌ 未找到匹配论文")
        sys.exit(0 if meta else 1)

    if args.input:
        path = Path(args.input)
        if not path.exists():
            print(f"Error: file not found: {path}")
            sys.exit(1)
        print(f"验证 {path.name} 中的参考文献...\n")
        results = verify_bibtex(path)
        print(f"\n结果: {results['verified']}/{results['total']} 验证通过, {results['failed']} 失败")
        rate = results['failed'] / max(results['total'], 1)
        if rate > 0.2:
            print(f"\n⚠️  验证失败率 {rate:.0%}，超过 20% 阈值！")
            print("建议: 检查参考文献来源，确保引用的是真实论文。")
        sys.exit(0 if results['failed'] == 0 else 1)

    parser.print_help()


if __name__ == '__main__':
    import urllib.parse
    main()