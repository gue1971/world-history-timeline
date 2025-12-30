import re
import collections

def analyze_and_clean_tags(file_path, threshold=2, execute=False):
    """
    JSファイル内のFULL_DATAからタグを抽出し、出現回数がthreshold未満のものをリストアップ、
    または実際に削除する。
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"エラー: {file_path} が見つかりませんでした。")
        return

    # FULL_DATA = [ ... ] の中身を抽出
    match = re.search(r'const FULL_DATA = \[(.*)\];', content, re.DOTALL)
    if not match:
        print("FULL_DATAが見つかりませんでした。")
        return

    data_str = match.group(1).strip()
    
    # イベント行からタグリスト部分を抽出する正規表現
    tag_pattern = r'\[\s*(-?\d+)\s*,\s*\'(.*?)\'\s*,\s*\'(.*?)\'\s*,\s*\[(.*?)\]'
    events = re.findall(tag_pattern, data_str, re.DOTALL)

    # 1. 全タグの出現回数をカウント
    all_tags = []
    for event in events:
        tag_list_str = event[3]
        # 'タグ1','タグ2' 形式をパース
        tags = [t.strip().strip("'").strip('"') for t in tag_list_str.split(',') if t.strip()]
        all_tags.extend(tags)

    tag_counts = collections.Counter(all_tags)
    
    # 削除対象（閾値未満）と維持対象を分ける
    to_remove_counts = {tag: count for tag, count in tag_counts.items() if count < threshold}
    to_keep_counts = {tag: count for tag, count in tag_counts.items() if count >= threshold}
    
    # --- レポート表示 ---
    print(f"=== タグ分析レポート (閾値: {threshold}回) ===")
    print(f"全ユニークタグ数: {len(tag_counts)}")
    print(f"維持されるタグ数: {len(to_keep_counts)}")
    print(f"消去対象のタグ数: {len(to_remove_counts)}")
    print("-" * 40)
    
    if to_remove_counts:
        print("【消去対象タグ一覧】")
        # 出現回数、名前の順でソートして表示
        sorted_remove = sorted(to_remove_counts.items(), key=lambda x: (x[1], x[0]))
        for tag, count in sorted_remove:
            print(f"  - {tag} ({count}回)")
    else:
        print("消去対象のタグはありません。")
    print("-" * 40)

    if not execute:
        print("※現在は『確認モード』です。実際にファイルを更新するには execute=True に書き換えてください。")
        return

    # 2. データの置換処理（execute=True の場合のみ）
    to_remove_set = set(to_remove_counts.keys())
    
    def replace_tags(match):
        prefix = match.group(1) 
        tag_content = match.group(2)
        suffix = match.group(3)
        
        tags = [t.strip() for t in tag_content.split(',') if t.strip()]
        cleaned_tags = []
        for t in tags:
            clean_t = t.strip("'").strip('"')
            if clean_t not in to_remove_set:
                cleaned_tags.append(t)
        
        return f"{prefix}[{', '.join(cleaned_tags)}]{suffix}"

    pattern = r'(\[\s*-?\d+\s*,\s*\'.*?\'\s*,\s*\'.*?\'\s*,\s*)\[(.*?)\](.*?\])'
    new_content = re.sub(pattern, replace_tags, content, flags=re.DOTALL)

    output_path = file_path.replace('.js', '_cleaned.js')
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"クリーンアップ完了: {output_path} を作成しました。")

if __name__ == "__main__":
    # 第一引数: ファイル名
    # threshold: この回数「未満」のタグを消す（2なら1回のものが消える）
    # execute: Trueにすると実際にファイルを書き出す
    analyze_and_clean_tags('data.js', threshold=500, execute=False)