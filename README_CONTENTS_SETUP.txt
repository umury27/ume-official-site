CONTENTS 設定について

GAME: ご指定の再生リストURL（list=PLXx6i1BN-blk）を使用。短いIDに見えるため、リンク先が正常か公開前に確認してください。
MUSIC: https://youtu.be/BjZd001ztbg
SHORTS: YouTube @u0_um の公開済み短尺動画からランダム表示。

【自動更新の設定】
1. GitHub にHPファイル一式（.github/workflows/ 以下を含む）をアップロード。
2. Google Cloud Console でプロジェクトを作成し YouTube Data API v3 を有効化。APIキーを作成。
3. GitHub リポジトリ Settings > Secrets and variables > Actions > New repository secret で名前 YOUTUBE_API_KEY にAPIキーを登録。HTMLにキーを貼らない。
4. GitHub Actions の Update Shorts list を手動実行。以降は毎日自動更新。
5. GitHub Pages の公開ブランチに shorts.json が配信されていることを確認。

注意: YouTube Data API にはShorts判定専用の項目がありません。この実装では直近の公開動画のうち180秒以下の動画を候補にします。そのため通常の短い動画が混ざる可能性があります。また検索結果は最大150件までです。APIキー未設定時や取得失敗時はShortsチャンネル一覧へのリンクを表示します。
