# FX研究 引き継ぎ書（2026-10-09）

この文書は新しいChatGPTチャットへ作業を移しても、過去の調査を重複させず、実装状態や未完了事項を誤認せずに継続するための正本。**このファイルとリポジトリ内のコード・データ・レポートを会話メモリより優先する。**

## 0. 新しいチャットで最初に行うこと

1. この文書を読み、リポジトリ `rikuudon24-beep/chair-scale` の `main` と `fx-h1-research` を確認する。
2. 直近のGitHub Actions実行結果、ワークフロー、共通仕様、状態台帳を読み、現在値を確認する。過去ログの要約だけで現状を断定しない。
3. **調査済み事項を重複して調査しない。** 新しい調査を始める前に既存のレポート・コード・CSV・コミット履歴を検索する。
4. 小分けの進捗報告や「続けていい？」の確認で止まらず、実装・テスト・保存を可能な範囲で自律的に進める。重要な節目だけ報告する。
5. 実装できていないものを完成扱いしない。検証が不足していれば不足と明記して継続する。

## 1. プロジェクト目標・ユーザー要望

- 最終目標：複数通貨ペアの高確度なエントリー・決済条件を多角的に研究し、条件成立時にユーザーへ通知するFX研究・監視システムを作る。
- テクニカル指標、マルチタイムフレーム、価格構造、ボラティリティ、ポジショニング・マクロ等を必要に応じて活用する。
- 無料・低コスト、スマートフォン中心の運用を優先する。
- 研究成果は逐一、リポジトリ内のルール、コード、データ、レポートとして保存する。
- 重複調査をしない。調査結果は「どの条件・期間・通貨ペア・コスト・OOS」で得られたかを残す。
- ユーザーは「早く終わらせるための完成扱い」を望んでいない。必要な検証を終えることを優先し、未検証・小標本は正直に報告する。
- 1つの戦略を無理に全通貨ペアへ一般化しない。JPY系や通貨ペア固有で有効なら、その範囲を明記する。
- エントリー通知だけでは完成ではない。**全戦略に、エントリー後の追跡・決済判定・決済通知・永続記録・再実行耐性を必須化する。**
- ユーザーは新チャットへの引き継ぎを強く重視する。正本ファイルを更新し続ける。

## 2. GitHubの正本

- Repository: `rikuudon24-beep/chair-scale`
- 実行ワークフローとライブ監視コード：`main`
- H1研究成果・ライブ状態：`fx-h1-research`
- H1の運用ルール：`research/h1/results/H1_V1_OPERATIONAL_RULES.md`（研究ブランチ側）
- 全体の決済通知設計：`research/notifications/FX_UNIFIED_LIFECYCLE_NOTIFICATION_SPEC.md`（main）
- 本引き継ぎ：`research/notifications/FX_RESEARCH_HANDOFF_2026-10-09.md`（main）
- ユーザー提供の元設計資料：`FX通知フロー設計.txt`。調査方針や最終通知条件を変える前に参照する。

関連するワークフロー：
- `.github/workflows/fx-h1-live-monitor.yml`：H1 v1ライブ監視、毎時 :11 UTC、state/alert保存、GitHub Issue通知。
- `.github/workflows/fx-current-notification-state.yml`：H4エントリー状態、毎時 :07 UTC、現状は主に候補・エントリー通知。
- `.github/workflows/fx-position-exit-monitor.yml`：別管理のH4決済監視、毎時 :17 UTC、`config/active_positions.json` を参照。
- `.github/workflows/fx-notification-replay.yml`：通知リプレイ検証。
- `.github/workflows/fx-unified-trade-engine.yml`、`fx-operational-validation.yml`、`fx-entry-timing.yml`、`fx-h1-research-data.yml` なども必要に応じて確認。

**GitHub Issuesは現状の永続通知チャネルであり、ChatGPTへの直接プッシュ通知ではない。** 直接プッシュが実際に実装・受信検証されるまでは「対応済み」と言わない。

## 3. 統合ライフサイクル・決済通知仕様（最優先）

正本仕様：`research/notifications/FX_UNIFIED_LIFECYCLE_NOTIFICATION_SPEC.md`

必須フロー：
`CANDIDATE -> ENTRY_PENDING -> OPEN -> EXIT_PENDING -> CLOSED`

追加状態：`REJECTED`、`CANCELLED`、`UNKNOWN`、`DELIVERY_PENDING`、`ERROR`。ポジション状態と通知配送状態は別々に管理する。データ不備・監視失敗を「決済条件なし／HOLD」と誤認させない。

共通台帳には少なくとも次を持たせる：
- `trade_id`、`strategy_id`、`strategy_version`、通貨ペア、時間足、方向
- シグナル時刻、エントリー時刻・価格、初期TP/SL、決済方針、時間制限
- 状態、最終確認済みバー、データソース
- 決済時刻・価格・理由、算出可能ならpips/Rとコスト控除後損益
- 作成・更新・クローズ時刻

共通イベント/outboxには、決定的な `event_id`、`trade_id`、イベント種別、価格・理由、TP/SL、配信状態、試行回数、最終試行時刻、配信確認時刻、エラーを保存する。イベントを永続記録してから配信する。同じイベントの二重通知を防ぐ。

決済評価の必須事項：
1. 原則、確定足のみを使う。
2. 最終足だけでなく、前回チェックから今回までの**全確定足**を処理する。
3. TP/SL、戦略固有決済、TIME、手動決済を戦略ごとの凍結ルールに沿って評価。
4. 同一足でTP/SL両方に触れ、下位足で順序を判別できない場合は保守的にSL優先と記録。
5. TIME決済は指定ホライズン足の終値で評価する。
6. 古い・欠損・矛盾したデータでは `UNKNOWN` / 監視劣化を通知する。HOLD判定にしない。
7. CLOSED記録は消さない。次回実行で再オープン・二重決済通知しない。
8. ワークフロー再起動後もポジションと未配信イベントを復元する。
9. 失敗時の診断Issueに実行ID、ペア、最終確定足、エラーを残す。
10. 実際のブローカー約定ではないシグナル価格・TP/SL想定価格を「約定価格」と表現しない。

最低限の回帰テスト：ENTRY一回、TP、SL、戦略固有EXIT、TIME、実行スキップ中の中間TP/SL、同一足TP/SL、再実行時の重複なし、配信失敗後の安全な再試行、古いデータでUNKNOWN、再起動後の状態維持、未配信EXITの回収、JPY/非JPY pip精度、合成取引のENTRY→EXIT→永続化→通知までのE2E。テスト失敗でワークフローも失敗させる。

## 4. H1 v1 凍結ルール

詳細正本：`research/h1/results/H1_V1_OPERATIONAL_RULES.md`

| Pair | Signal | Entry | TP | SL | Horizon |
|---|---|---|---:|---:|---:|
| EURJPY | trend_down & d1_bull & rsi_up6 & dist_ema20<=0 & body_range>=0.6 | 次のH1始値 | 100p | 40p | 72h |
| USDCHF | trend_down & d1_bull & rsi_up6 & adx>=25 & ema20_slope>=0 | 1本確認後 | 40p | 40p | 48h |
| AUDNZD | trend_down & h4_bull & d1_bull | 次のH1始値 | 60p | 75p | 72h |

定義：
- `trend_down`: H1 EMA20 < EMA50 < EMA200
- `d1_bull` / `h4_bull`: シグナル時点で確定済みの直前HTF足が陽線
- `rsi_up6`: RSI14現在値 - 6本前 > 3
- `dist_ema20`: (close - EMA20) / ATR14
- `body_range`: abs(close-open)/(high-low)
- `adx`: H1 ADX14
- `ema20_slope`: H1 EMA20の1本変化率
- `confirm_1bar`: 次のH1終値がシグナル足高値を上抜けて確定したら、その次のH1始値でエントリー
- TP/SLは実際のエントリー価格基準。時間切れはホライズン足終値。同一足TP+SLはSL優先。
- ペアごとに非重複ライフサイクル。
- v1ルールはライブ結果に合わせて変更しない。変更時はv1.1とし、別の時系列検証を行う。

除外：
- USDJPY：採掘フィルタのOOSが2件のみで不十分。
- GBPJPY：5pコスト後は限界的。
- AUDUSD：凍結候補がOOSで不合格。

Pristine holdout cutoff：2026-09-30 22:00 UTC。直近の確認ではEURJPY/AUDNZDともサンプル不足。これは合格でも不合格でもない。

## 5. H1モニター実装状態（2026-10-09確認）

関連コード：`research/h1/scripts/monitor_h1_live.py`、`download_h1_live.py`、`download_htf_live.py`。テスト：`research/h1/scripts/test_monitor_h1_lifecycle.py`。

すでに入っている修正：
- 最新の確定H1足を評価（1本遅れの不具合を修正）。
- H1が古い場合はfail-safe。
- H4/D1は更新後の同じH1データから再構成。
- OPENポジションは前回チェック以降の全確定H1足を走査し、中間のTP/SLを取りこぼさない。
- 同一足TP/SLはSL優先。
- TIME exitは指定ホライズン足の終値。
- CLOSED行をpositions ledgerに残す。
- ENTRY/EXITアラートIDを用いた重複防止。
- stateは `fx-h1-research` ブランチに保存。GitHub Issueは永続イベント通知。
- テスト失敗をworkflow成功として隠さないよう、テスト前に `set -euo pipefail` を設定。

直近確認：
- Actions run `37868287986`（2026-10-09、commit `4f1b67e...`）は成功。テスト7件すべて成功、state publish・Issue publish・artifact uploadも成功。
- 7テスト：中間TP/SL捕捉、confirm_1bar失敗、confirm_1bar成功、partial D1 rowがない場合のprior、HTF prior選択、同一足TP/SL+closed persist、TIME exit。
- ログの最終ライブ判定ではEURJPY/USDCHF/AUDNZDともsignal=False、NEW ALERTS 0。
- 研究ブランチのstateファイルは最新確認時点でヘッダーのみ（open trade/alertなし）。
- これは現状のコード経路と合成テストの成功。実際の相場でENTRYからEXITまで通した実績も、ユーザー端末へのpush受信もまだ証明していない。

ライブデータ：
- Yahoo Finance chart APIを標準urllibで使用。
- EURJPY -> `EURJPY=X`; USDCHF -> `CHF=X`; AUDNZD -> `AUDNZD=X`。
- 直近14日H1。H4/D1はH1から再サンプリング。
- overlap guard: 直近72hで最低24本、終値差中央値<=3pips、p95<=10pips。更新後データが2h超古い場合は失敗。
- Yahooはライブ用の公開データでブローカー価格と同一ではない。ソース変更はライブ用に限定し、過去の凍結研究データは改変しない。

## 6. 他のH4監視はまだ共通化されていない

`scripts/monitor_notification_state.py` は確定H4足からGC/DC、20EMAタッチ、ブレイク条件を評価して候補/ENTRYアラートを生成するが、単独では共通台帳を使ったポジション追跡・TP/SL/TIMEクローズを完成させていない。

`scripts/monitor_position_exit.py` は `config/active_positions.json` のopenポジションを読み、50pips到達後の価格20EMA逆クロス＋DIスプレッド条件を評価する別系統。H1台帳とは別管理。これを共通ライフサイクル台帳に統合することが必要。現状のexit monitorにはIssue一覧が最初の100件のみの箇所や、状態のcommit/push競合耐性なども確認・改善候補として残る。

`scripts/publish_notification_issues.py` にはページネーション、リトライ、POST応答が曖昧な場合の重複防止がある。H1のpublisherも全Issueページを確認する。これらのパターンを共通dispatcherに統合し、個々のworkflowで異なる実装を増やさない。

## 7. B + EMA20研究（本番承認は未了）

レポート：`reports/b_ema20_rolling_robustness_2026-10-08.md`

固定条件：
- signal_range_atr <= 1.151613
- bars_touch_to_signal <= 6
- 既存シグナルのentry_timestamp/entry_price
- 初期SL：Longはtouch candle low、Shortはtouch candle high
- Exit：SL -> EMA20逆クロス -> 最大20本TIME
- H4 EMA20はcloseから逐次計算
- パラメータ最適化はしない

全体 N=98、WR 39.8%、平均+10.2pips、PF 1.471、合計+1002.9pips。
Discovery N=63、WR 36.5%、平均+3.3pips、PF 1.137。
Validation N=22、WR 36.4%、平均+12.9pips、PF 1.645。
OOS N=13、WR 61.5%、平均+39.3pips、PF 4.193。

2021–22のローリング窓は弱く、2023以降はおおむね良好。レジーム依存の疑いが強い。**候補であって本番承認ではない。閾値は変えず**、ATR、EMA傾き、トレンド強度、レンジ/トレンド判定などで効く相場・失敗する相場を調べる。

別の閾値安定性結果（threshold 0.10）は全体N=52 WR55.8%、平均+29.0pips、PF3.00、Discovery N=34 PF2.31、Validation N=11 PF5.32、OOS N=7 PF6.67。サンプルが小さいため本番承認しない。

## 8. 過去のexit候補OOS結果（文脈保存）

- USDJPY: pullback_reversal_rsi / break_signal_high / TP40 SL40 H72; OOS n=23, WR .565, PF1.300, ExpR .130, NetR 3.00.
- EURJPY: pullback_reversal_rsi / next_open / TP100 SL40 H72; OOS n=29, WR .379, PF1.833, ExpR .431, NetR 12.5.
- GBPJPY: pullback_reversal / break_signal_high / TP40 SL50 H24; OOS n=32, WR .531, PF1.133, ExpR .050, NetR 1.6.
- USDCHF: pullback_reversal_rsi / confirm_1bar / TP40 SL40 H48; OOS n=30, WR .400, PF1.714, ExpR .167, NetR 5.0.
- AUDUSD: OOS negative; reject.
- AUDNZD: pullback_reversal / next_open / TP60 SL75 H72; OOS n=19, WR .632, PF4.8, ExpR .400, NetR 7.6.

Final cost/neighborhood robustness:
- EURJPY validation PF/ExpR at 3p = 1.805/.481; at 5p = 1.689/.431; robust neighbors 50/81.
- EURJPY OOS 3p = 1.763/.425; 5p = 1.642/.375; robust neighbors 81/81.
- AUDNZD validation 3p = 1.362/.074; 5p = 1.217/.047; robust neighbors 31/81.
- AUDNZD OOS 3p = 3.067/.364; 5p = 2.860/.337; robust neighbors 78/81.
- Universal H1 candidate was not robust OOS; pair-specific strategy routing is preferred.

## 9. 次に実施する作業（順番を守る）

### P0 — 共通ライフサイクル実装
1. 全ワークフロー・全戦略が生成するentry/exit/alertデータのスキーマを調べ、重複ソース・状態の不整合をマッピングする。
2. 共通trade ledger + durable event outbox + idempotent dispatcherの仕様をコード化する。GitHub CSV/Issuesを当面の永続層として使う場合も、更新競合と原子的整合性の問題を設計・テストする。
3. 既存H1モニターを共通スキーマへ移行。移行前後のopen/closed stateを照合し、既存の履歴を無断削除しない。
4. H4 entry candidateとH4 exit monitorを共通台帳へ統合。strategy-specific exit adapterを持たせ、各戦略の出口ルールを混同しない。
5. 合成取引でENTRY->TP/SL/TIME/strategy exit->persist->Issue作成->再実行時重複なしをE2E検証。
6. 古いデータ、API障害、通知失敗、競合push、再起動、alertはあるがtradeがない不整合の回復をテスト。
7. ChatGPT直接プッシュの利用可能な正式経路を調査し、実装・受信証拠がない間はGitHub Issue通知と明確に区別する。

### P1 — 研究
8. B+EMA20のレジーム依存要因を、事前に定めた特徴量と時系列分割で調査。閾値を後付け最適化しない。
9. Pristine holdoutはサンプルが蓄積するまで別管理。サンプル不足を合否判定に使わない。
10. 元設計資料の大口/マクロ要因（CFTC COT、net position変化、OI、Z-score、金利差、中央銀行政策、主要経済指標、BIS REERなど）は、無料公開データ優先で、取得頻度・欠損・公表ラグを考慮して統合を検討する。

## 10. 完成判定ゲート

「完成」と呼ぶ前に全て確認：
- 全ENTRYが一意のtrade_idで永続化され、戦略ごとのexit policyへ接続している。
- TP、SL、戦略固有EXIT、TIMEのそれぞれで決済状態・理由・価格/時刻を記録し、ユーザー通知を生成する。
- 監視停止・スキップ・再起動後も中間バーを処理し、未配信イベントを回収する。
- 重複通知・二重クローズ・閉じた取引の再オープンがない。
- stale/missing dataはUNKNOWNとして報告し、HOLD/no-exitと誤認させない。
- 合成E2Eテストが成功し、GitHub Actionsがテスト失敗時に失敗する。
- GitHub Issue通知は成功ログがあり、必要ならIssue実物を確認する。
- ChatGPT pushは実際の受信確認がある場合のみ対応済みとする。
- OOS・コスト・隣接パラメータ・レジーム・サンプル数の検証が揃わない戦略は本番承認しない。

## 11. 直近の関連コミット / 実行

- Unified lifecycle spec added: `1bd593d6280f603312b551223da7febf8aadf4bc`
- H1 tests fail workflow when regression tests fail: `4f1b67e258056a57167c8e12a8708e3fc9c06aff`
- H1 lifecycle fixes include missed intermediate bars: `cd07f72d739471e90c82b18ab8d145ab93355998`
- Preserve closed lifecycle rows: `e523453c533675b3f2b2b0791524a59df7e57470`
- H1 run `37868287986`: https://github.com/rikuudon24-beep/chair-scale/actions/runs/37868287986
- B + EMA20 report: https://github.com/rikuudon24-beep/chair-scale/blob/main/reports/b_ema20_rolling_robustness_2026-10-08.md

## 12. 新しいチャットに貼る開始プロンプト

あなたはFX研究プロジェクトの継続担当です。まずGitHubリポジトリ `rikuudon24-beep/chair-scale` の `research/notifications/FX_RESEARCH_HANDOFF_2026-10-09.md` と `research/notifications/FX_UNIFIED_LIFECYCLE_NOTIFICATION_SPEC.md` を読み、mainとfx-h1-researchの現状、直近Actions、state/alert台帳を実際に確認してください。記載内容は引き継ぎ時点のスナップショットなので、現在値は必ず再確認してください。完了済み調査を繰り返さず、未完了のP0「共通ライフサイクル台帳・event outbox・通知dispatcherの実装と、H1/H4全系統への統合」から継続してください。すべての戦略にENTRYからTP/SL/戦略固有EXIT/TIMEまでの追跡・通知・永続化・再起動復旧を必須化してください。テストを実行し、失敗は直して再実行してください。未検証を完成扱いせず、ChatGPT直接pushも実際に受信確認するまで未実装と明記してください。調査・コード・結果はリポジトリへ保存し、重複調査を避け、重要な節目だけ日本語で報告してください。
