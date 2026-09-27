<div align="center">

# muse-cli

[English](README.md) | [한국어](README.ko.md)

터미널에서 개인 muse.ai AI 에이전트와 대화하세요.

[![PyPI](https://img.shields.io/pypi/v/muse-cli?style=for-the-badge)](https://pypi.org/project/muse-cli/)
[![Python](https://img.shields.io/pypi/pyversions/muse-cli?style=for-the-badge)](https://pypi.org/project/muse-cli/)
[![Downloads](https://img.shields.io/pepy/dt/muse-cli?style=for-the-badge)](https://pepy.tech/project/muse-cli)
[![License: MIT](https://img.shields.io/github/license/nikships/muse-cli?style=for-the-badge)](https://github.com/nikships/muse-cli/blob/main/LICENSE)
[![GitHub stars](https://img.shields.io/github/stars/nikships/muse-cli?style=for-the-badge)](https://github.com/nikships/muse-cli/stargazers)
[![Website](https://img.shields.io/badge/website-live-3fb950?style=for-the-badge)](https://muse-cli-site.web.app)

![muse-cli hero](https://raw.githubusercontent.com/nikships/muse-cli/main/assets/hero.webp)

</div>

## 소개

muse.ai 개인 AI 에이전트를 위한 명령줄 클라이언트입니다. 브라우저 없이 터미널에서 대화하고, 스크립트로 자동화하고, 사이드챗, 피드, 목표, 아이디어, 세션을 관리할 수 있습니다. 앱 자체의 게이트웨이 프로토콜을 직접 사용합니다: HTTPS 인증, 후 개인 VM으로의 암호화된 Noise-XX WebSocket.

- **셸에서 대화:** 메시지를 보내고 에이전트의 답변을 JSON으로 받습니다.
- **스크립트 가능:** 모든 명령이 JSON을 출력하므로 `jq`, cron 작업, 다른 AI 에이전트와 연동됩니다.
- **전체 커버리지:** 일반 작업을 위한 명명된 명령과 258개 게이트웨이 메서드를 위한 `raw` 탈출구.
- **에이전트 준비:** 코딩 에이전트가 muse.ai 에이전트를 구동할 수 있는 에이전트 스킬 제공.

## 에이전트가 에이전트를 구동

코딩 에이전트에게 프롬프트를 제공하면 muse-cli 스킬을 활성화하고 읽기 전용 명령을 실행합니다. 아래는 Droid 워커가 `muse-cli status`와 `muse-cli goals`를 실행하고 보고하는 실제 세션입니다.

![Droid agent using muse-cli to check status and goals](https://raw.githubusercontent.com/nikships/muse-cli/main/assets/demo-agent.png)

## 에이전트 사이드챗 워크플로

어떤 터미널 기반 코딩 에이전트든 전용 Muse 사이드챗을 할당하여 웹 검색, 브라우징, 장기 작업을 Muse에 위임할 수 있습니다.

`agent` 명령 그룹은 기존 `session-start`, `send --thread`, `history --thread` 명령을 로컬 이름-스레드 레지스트리로 감쌉니다. 각 에이전트 이름은 하나의 지속적인 사이드챗 스레드에 매핑되며, `~/.config/muse-cli/agents.json`에 저장됩니다 (모드 644, 민감하지 않은 메타데이터만 — 쿠키, 토큰, 메시지 내용 없음).

```bash
muse-cli agent init opencode          # 사이드챗 생성 또는 재사용
muse-cli agent list                   # 모든 에이전트 + 스레드 상태 표시
muse-cli agent send opencode "research X" --wait 120
muse-cli agent history opencode --limit 10
```

### 전용 사이드챗이 필요한 이유

- **격리:** 각 에이전트의 컨텍스트가 분리됩니다 — OpenCode, Codex, Claude Code 대화 간 교차 오염이 없습니다.
- **지속성:** 스레드는 에이전트 재시작 후에도 유지됩니다. `agent init`을 다시 실행하면 같은 스레드를 재사용합니다.
- **감사 가능성:** `agent list`는 서버에서 삭제된 스레드를 표시하여 `agent init`으로 재바인딩할 수 있습니다.
- **단순성:** 스레드 ID를 수동으로 추적할 필요가 없습니다 — 레지스트리가 이름을 스레드로 자동 확인합니다.

## 빠른 시작

```bash
uv tool install muse-cli      # 또는: pipx install muse-cli   /   pip install muse-cli
```

명령은 `muse-cli`입니다. 많은 시스템에서 `muse` 이름은 Muse Code에 사용됩니다.

에이전트 스킬도 필요하신가요? 설치 프로그램이 CLI를 설정하고 스킬을 `~/.agents/skills/muse-cli`에 복사합니다:

```bash
curl -fsSL https://raw.githubusercontent.com/nikships/muse-cli/main/install.sh | bash
```

`muse-cli update`로 업그레이드하세요. 터미널에서 하루에 한 번 PyPI를 확인하고 새 릴리스가 있으면 해당 명령을 stderr에 출력합니다. 자동 업그레이드하지는 않습니다. `MUSE_NO_UPDATE_CHECK=1`로 알림을 무시할 수 있습니다. 출력이 파이프되거나 `CI`가 설정되면 확인이 조용해집니다. `uv tool uninstall muse-cli`로 제거합니다.

로그인은 별도의 일회성 단계입니다. Chrome은 원격 디버깅을 켠 후 쿠키를 공유합니다. 다른 명령을 실행하기 전에 [한 번 로그인](#한-번-로그인)을 따르세요.

## 한 번 로그인

muse-cli는 Chrome에 이미 있는 로그인을 사용하여 해당 쿠키를 `~/.config/muse-cli/cookies.txt`에 저장하고 (모드 600, 사용자만 읽을 수 있음) 이후 muse.ai와 직접 통신합니다. 액세스 토큰은 매 명령마다 새로 가져옵니다. 나중에 명령이 쿠키 만료를 알리면 이 섹션을 반복하세요.

순서대로 진행하세요. 각 단계는 계속하기 전에 자체 확인을 수행합니다.

### 1. 쿠키 리더 설치

`auth export`는 [agent-browser](https://github.com/vercel-labs/agent-browser)를 사용하여 Chrome의 쿠키를 읽습니다. 이 패키지는 npm에서 제공되므로 먼저 Node.js가 필요합니다.

```bash
node --version    # 실패하면 https://nodejs.org에서 Node.js LTS를 설치하고
                   # 새 터미널을 여세요
npm i -g agent-browser
agent-browser --version
```

`npm i -g`은 npm의 전역 bin 디렉터리에 쓸 권한이 필요합니다. `EACCES` 오류가 발생하면 다음 중 하나를 선택하여 사용하세요: [소유한 npm 프리픽스 구성](https://docs.npmjs.com/resolving-eacces-permissions-errors-when-installing-packages-globally) 또는 다른 전역 npm 도구와 동일한 권한으로 설치를 실행하세요. 그런 다음 `command -v agent-browser`가 경로를 출력하는지 확인하세요.

### 2. Chrome이 쿠키를 공유하도록 설정

**Google Chrome**을 열고, muse.ai에 사용하는 동일한 프로필에서 주소 표시줄에 다음을 붙여넣으세요:

```
chrome://inspect/#remote-debugging
```

원격 디버깅을 켭니다. 체크박스는 **이 브라우저 인스턴스에 대한 원격 디버깅 허용**이라고 표시됩니다. Chrome을 열어 두세요.

Chrome이 이미 열려 있고 muse.ai가 로드된 상태에서 이 설정을 켜세요. 내보내기는 스위치가 켜진 후에만 해당 창을 볼 수 있습니다. 이 페이지는 Chrome 144 이상에 있습니다.

이 창에 머물러 있으세요. `--remote-debugging-port`로 두 번째 Chrome을 시작하면 다른 프로필이 열리며, 그 프로필에는 muse.ai 로그인이 없습니다.

### 3. muse.ai 탭에 로그인

같은 Chrome 창에서 https://muse.ai/를 열고 로그인하세요. 탭을 열어 두세요. 내보내기는 활성 탭을 읽으므로 다음 명령을 실행할 때 muse.ai 탭이 앞에 있어야 합니다.

### 4. 로그인 저장

```bash
muse-cli auth export
```

Chrome이 디버깅 연결을 허용할 수 있습니다. **허용**을 클릭하세요. 명령이 이미 실패한 경우 허용을 클릭한 후 다시 실행하세요.

성공 시 다음과 같이 표시됩니다 (개수는 다를 수 있음):

```
saved 12 muse.ai cookies to /home/you/.config/muse-cli/cookies.txt
```

명령은 실패 시 수정 방법을 직접 출력합니다. 인식되는 것들은 다음과 같습니다:

| 출력 내용 | 수정 방법 |
| --- | --- |
| 실행 중인 Chrome 없음 / 원격 디버깅 | 2단계의 스위치가 꺼져 있습니다. 이미 열어 둔 Chrome에서 켜고 명령을 다시 실행하세요. |
| muse.ai 탭 없음 | 3단계. 같은 창에서 https://muse.ai/를 열고 탭을 열어 두세요. |
| `hatch_sess` 없음 | 탭이 열려 있고 로그아웃 상태입니다. 로그인한 후 다시 내보내세요. 디스크에 있는 쿠키 파일은 그대로 유지됩니다. |
| `agent-browser` 설치되지 않음 | 1단계. `node --version`, 그런 다음 `npm i -g agent-browser`, 그런 다음 새 터미널. |
| 데몬이 이미 실행 중 | 이전 시도가 멈췄습니다. `agent-browser close`, 그런 다음 `muse-cli auth export`. |

### 5. 연결 확인

```bash
muse-cli status
```

VM ID, 채팅 수, 읽지 않은 수, 신원 정보가 포함된 JSON을 받습니다. 설치와 로그인이 모두 성공했음을 의미합니다.

### 쿠키를 직접 복사

Node가 없거나 원격 디버깅을 켜고 싶지 않을 때 사용하세요.

1. Chrome에서 https://muse.ai/를 열고 로그인하세요.
2. DevTools (F12 또는 Ctrl+Shift+I) → **애플리케이션** → **쿠키** → `https://muse.ai`를 여세요.
3. 쿠키를 한 줄에 복사하세요. `hatch_sess`가 있어야 합니다. 쿠키는 `; ` (세미콜론, 공백)으로 구분하세요. Netscape 쿠키 저장소 (curl이 쓰는 형식)와 JSON 객체 (예: `{"hatch_sess": "..."}`)도 작동합니다.

```bash
mkdir -p ~/.config/muse-cli
printf '%s\n' 'hatch_sess=the-value-from-devtools; other_cookie=other_value' > ~/.config/muse-cli/cookies.txt
chmod 600 ~/.config/muse-cli/cookies.txt
muse-cli status
```

## 사용법

```bash
muse-cli threads                                  # 메인 채팅 + 사이드챗
muse-cli history --limit 5                        # 최근 메시지
muse-cli history --thread <session-id> --limit 5  # 사이드챗 하나
muse-cli send "summarize my unread" --wait 120    # 메시지 전송 + 답변 대기
muse-cli watch --timeout 60                       # 실시간 에이전트 이벤트 추적

muse-cli feed --limit 5
muse-cli feed-react <unit-id> love
muse-cli goals
muse-cli ideas
muse-cli idea-exec <idea-id>                      # 에이전트가 아이디어를 실행
muse-cli session-start --title "trip planning"    # 새 사이드챗
muse-cli session-rename <id> "new title"
muse-cli session-archive <id>                     # 또한: pin, unpin, unarchive, delete
muse-cli seen <thread-id>
muse-cli wake
muse-cli raw <method> --body '{}'                 # 탈출구: 258개 게이트웨이 메서드 중 아무거나
```

모든 명령이 JSON을 출력합니다. VM은 세션에서 자동 발견되고, 임의의 장치 ID가 첫 실행 시 생성됩니다.

다른 도구와 파이프:

```bash
muse-cli send "what's on my calendar today?" | jq -r .reply.text
```

## 에이전트 명령

`agent` 명령 그룹은 이름이 지정된 사이드챗 스레드를 관리합니다. 기존 `session-start`, `send --thread`, `history --thread` 명령을 감쌉니다 — 이들은 그대로 유지되며 단독으로도 완전히 기능합니다.

```bash
muse-cli agent init <name> [--title "optional title"]
muse-cli agent list
muse-cli agent send <name> <text> [--wait N]
muse-cli agent history <name> [--limit N] [--raw]
```

- `init`은 멱등적입니다: 이름이 이미 존재하고 스레드가 살아 있으면 재사용하고, 그렇지 않으면 새 사이드챗을 생성합니다.
- `send`와 `history`는 이름을 스레드 ID로 자동 확인합니다. 알 수 없는 이름은 코드 2로 종료되고, 서버에서 삭제된 스레드는 코드 3으로 종료됩니다.
- 레지스트리는 `~/.config/muse-cli/agents.json`에 저장됩니다 (모드 644). 이름, 스레드 ID, 제목, 타임스탬프만 저장합니다 — 쿠키, 토큰, 메시지 내용은 절대 저장하지 않습니다.
- Windows, macOS, Linux에서 작동합니다. `MUSE_CLI_CONFIG_DIR`로 설정 디렉터리를 재정의할 수 있습니다.

### OpenCode 예제

```bash
# OpenCode 세션에서 에이전트에게 전용 지속 사이드챗 할당:
muse-cli agent init opencode --title "OpenCode research"

# 연구 작업을 보내고 답변을 기다림:
muse-cli agent send opencode "Find the latest stable release of curl_cffi and summarize breaking changes" --wait 120

# 대화 기록 확인:
muse-cli agent history opencode --limit 5
```

### Codex CLI 예제

```bash
# Codex CLI 세션에서:
muse-cli agent init codex --title "Codex delegated tasks"

# 브라우징 작업 위임:
muse-cli agent send codex "Browse https://example.com and extract the pricing table" --wait 90

# 에이전트가 찾은 것을 검토:
muse-cli agent history codex --limit 3
```

### Claude Code 예제

```bash
# Claude Code 세션에서:
muse-cli agent init claude --title "Claude web research"

# 장기 연구 작업 위임:
muse-cli agent send claude "Research the top 3 vector databases for Python and compare their licenses" --wait 180

# 결과 확인:
muse-cli agent history claude --limit 5
```

### Gemini CLI 예제

쉘 명령을 실행할 수 있는 모든 터미널 기반 에이전트에 동일한 패턴이 적용됩니다:

```bash
muse-cli agent init gemini --title "Gemini research"
muse-cli agent send gemini "Search for recent changes to the Python GIL" --wait 120
muse-cli agent history gemini --limit 5
```

스레드 ID는 로컬 레지스트리에서 자동 확인됩니다 — 에이전트는 스레드 ID를 알거나 추적할 필요가 없습니다. 기본 `send --thread`, `session-start`, `history --thread` 명령은 직접 사용을 위해 완전히 기능합니다.

## 작동 원리

![how muse-cli connects](https://raw.githubusercontent.com/nikships/muse-cli/main/assets/how-it-works.webp)

![muse-cli connection flow](https://raw.githubusercontent.com/nikships/muse-cli/main/assets/flow.webp)

전체 프로토콜 노트(메서드 테이블과 리버스 엔지니어링 중 발견된 서버 특이 사항 포함)는 [docs/PROTOCOL.md](https://github.com/nikships/muse-cli/blob/main/docs/PROTOCOL.md)를 참조하세요.

## 문서

| 리소스 | 설명 |
|----------|-------------|
| [skills/muse-cli/SKILL.md](https://github.com/nikships/muse-cli/blob/main/skills/muse-cli/SKILL.md) | 에이전트 스킬: 설치 확인, 인증 설정, 명령 참조 |
| [docs/PROTOCOL.md](https://github.com/nikships/muse-cli/blob/main/docs/PROTOCOL.md) | 게이트웨이 프로토콜 참조: 인증 체인, Noise 전송, 프레이밍, 메서드 특이 사항 |
| [routes.json](https://github.com/nikships/muse-cli/blob/main/src/muse_cli/routes.json) | 경로와 서비스가 있는 258개 게이트웨이 메서드 |
| `muse-cli raw --help` | 모든 게이트웨이 메서드를 직접 호출하는 탈출구 |

## 개발

```bash
git clone https://github.com/nikships/muse-cli.git
cd muse-cli
uv run muse-cli --help
```

```
muse-cli/
assets/              README 아트워크 (Muse Image로 생성)
docs/PROTOCOL.md     재유도를 위한 프로토콜 참조
skills/muse-cli/     에이전트 스킬
src/muse_cli/
  cli.py             인자 파싱과 모든 명령
  gateway.py         게이트웨이 클라이언트 (인증, Noise 전송, 구독)
  routes.json        웹 클라이언트에서 추출한 258개 게이트웨이 메서드
  desc0.bin          와이어 프레이밍을 위한 protobuf 디스크립터
  desc1.bin
install.sh           CLI + 스킬 설치 프로그램
pyproject.toml
```

## 설정 노트

- 로그인은 위의 [한 번 로그인](#한-번-로그인) 섹션입니다. 쿠키는 `~/.config/muse-cli/cookies.txt`에 저장됩니다 (모드 600). 액세스 및 게이트웨이 토큰은 매 실행 시 새로 가져옵니다.
- `auth export`는 [agent-browser](https://github.com/vercel-labs/agent-browser)를 통해 Google Chrome에서 해당 쿠키를 읽습니다. Chrome이 열려 있고 원격 디버깅이 켜져 있어야 하며 (`chrome://inspect/#remote-debugging`) 로그인한 muse.ai 탭이 앞에 있어야 합니다.
- muse.ai의 이용 약관과 속도 제한을 존중하세요. 내부 API는 버전이 없고 변경될 수 있습니다. 호출이 실패하면 새 앱 번들에서 다시 유도하세요.

## 기여

이슈와 PR을 환영합니다. 프로토콜이 변경되면 가장 유용한 기여는 어떤 메서드가 깨졌는지와 새 서버 오류 텍스트를 알려주는 것입니다.

<a href="https://github.com/nikships/muse-cli/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=nikships/muse-cli" />
</a>

## 추천 코드

선택적 추천 코드가 있습니다: `W09QZF`. muse-cli 또는 그 기능을 사용하는 데 **필수는 아닙니다**.

> **면책 조항:** 직접 Muse 브라우징을 통한 보상 조건 확인은 2026-09-27에 조직 정책에 의해 차단되었습니다. 보상 조건(수량, 자격, 기간)은 확인되지 않았으며 여기에 명시되지 않습니다. 현재 조건은 muse.ai에서 직접 확인하세요.

## 크레딧

[nikships/muse-cli](https://github.com/nikships/muse-cli)를 기반으로 / 포크한 프로젝트입니다. 원작자: [Nik](https://github.com/nikships). 원본 MIT 라이선스가 보존되었습니다.

에이전트 사이드챗 워크플로는 기존 `session-start`, `send --thread`, `history --thread` 명령을 감쌉니다 — 새로운 게이트웨이 메서드를 재구현하거나 발명하지 않습니다.

## 라이선스

MIT. [LICENSE](https://github.com/nikships/muse-cli/blob/main/LICENSE)를 참조하세요.

---

<div align="center">

[![Star History Chart](https://api.star-history.com/svg?repos=nikships/muse-cli&type=Date)](https://star-history.com/#nikships/muse-cli&Date)

</div>
