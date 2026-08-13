# CampusBot Offline for Windows

## 中文

这是一个适用于 64 位 Windows 10/11 的 CampusBot 离线包。包内已经包含 Windows Python 运行环境、Ollama、`qwen3:0.6b` 模型和 CampusBot 项目代码。

运行聊天功能不需要安装 Python、Docker 或 Ollama，不需要 API Key，也不需要在第一次启动时下载模型。

### 运行方法

1. 将整个 ZIP 文件完整解压，不要直接在 ZIP 预览窗口中运行。
2. 打开解压后的文件夹。
3. 双击 `Start CampusBot.cmd`。
4. 等待命令窗口显示 CampusBot 已经就绪。
5. 浏览器会自动打开 `http://127.0.0.1:8000/`。
6. 使用期间不要关闭启动命令窗口。
7. 使用结束后回到命令窗口按 Enter，程序会停止本地服务。

如果启动窗口被意外关闭，可以双击 `Stop CampusBot.cmd` 清理后台服务。

启动器会自动选择项目入口：存在 `CampusBot\serve.py` 时运行 `serve.py`，否则运行 `CampusBot\main.py`。因此可以从单文件程序逐步重构成多模块服务，而不需要手工修改启动命令。

Windows 如果显示安全提醒，请先确认 ZIP 来自可信的课程发布位置。必要时选择“更多信息”，再选择“仍要运行”。Ollama 和 Python 运行文件来自各自的官方发布包，但本课程组合包没有购买 Windows 代码签名证书。

### 项目代码

可阅读和修改的代码位于 `CampusBot` 文件夹。修改 `main.py`、`prompt.txt`、`knowledge.json` 或 `web` 中的文件后，停止并重新启动 CampusBot 即可看到变化。

可以在项目中继续增加 `app`、`skills`、`governance`、`tests`、`config` 和其他目录，实现技能路由、身份权限、安全规则、审计日志、对话状态及自动测试。

测试方法：在 `CampusBot\tests` 中添加 `test_*.py` 文件，然后双击 `Run Tests.cmd`。测试使用内置 Python 的 `unittest`，不需要启动 Ollama。

依赖方法：当前运行依赖已经安装，并在 `runtime\wheels` 中保留了离线 wheel。修改 `requirements.txt` 后可双击 `Install Offline Dependencies.cmd`。如果增加了包内没有的新第三方库，需要把适用于 Windows x64、Python 3.11 的 `.whl` 文件及其依赖放入 `runtime\wheels`，再运行该命令。

运行日志位于：

```text
%LOCALAPPDATA%\CampusBot Offline\logs\
```

系统要求：64 位 Windows 10/11，建议至少 8 GB 内存，并预留至少约 2 GB 解压空间。模型推理完全在本机完成，首次回答可能需要更长时间。此精简包以内置 CPU 运行组件保证通用性，不包含体积很大的 NVIDIA CUDA 加速库。

## English

This is an offline CampusBot package for 64-bit Windows 10/11. It includes a Windows Python runtime, Ollama, the `qwen3:0.6b` model, and the editable CampusBot project source.

Chat does not require installing Python, Docker, or Ollama. It does not need an API key or a model download on first launch.

### Run

1. Extract the entire ZIP. Do not run it from the ZIP preview window.
2. Open the extracted folder.
3. Double-click `Start CampusBot.cmd`.
4. Wait until the command window reports that CampusBot is ready.
5. The browser opens `http://127.0.0.1:8000/` automatically.
6. Keep the command window open while using CampusBot.
7. Return to the command window and press Enter when finished.

If the launcher window is closed unexpectedly, double-click `Stop CampusBot.cmd` to clean up the background services.

The launcher selects the project entry point automatically. It runs `CampusBot\serve.py` when that file exists; otherwise it runs `CampusBot\main.py`. This supports gradual refactoring from a single-file program to a modular service without manually changing the launch command.

If Windows shows a security warning, first confirm that the ZIP came from the trusted course distribution location. If needed, choose More info and then Run anyway. The Ollama and Python executables come from their official distributions, but this combined course package does not have a purchased Windows code-signing certificate.

Editable project files are in the `CampusBot` folder. Stop and restart CampusBot after changing `main.py`, `prompt.txt`, `knowledge.json`, or files under `web`.

The project can be extended with `app`, `skills`, `governance`, `tests`, `config`, and other directories for skill routing, identity and permissions, safety rules, audit logging, conversation state, and automated tests.

To test, add `test_*.py` files under `CampusBot\tests`, then double-click `Run Tests.cmd`. Tests use the bundled Python `unittest` module and do not require Ollama to be running.

Runtime dependencies are already installed, and their offline wheels are stored under `runtime\wheels`. After changing `requirements.txt`, double-click `Install Offline Dependencies.cmd`. For a new third-party library that is not bundled, add its Windows x64 Python 3.11 `.whl` file and dependency wheels to `runtime\wheels` before running the command.

Logs are stored in:

```text
%LOCALAPPDATA%\CampusBot Offline\logs\
```

Requirements: 64-bit Windows 10/11, at least 8 GB RAM recommended, and approximately 2 GB of free space for extraction. Model inference runs locally. The first response may take longer. For broad compatibility and a smaller package, this build includes the CPU runtime but omits the large NVIDIA CUDA acceleration libraries.

## 한국어

이 패키지는 64비트 Windows 10/11용 CampusBot 오프라인 패키지입니다. Windows Python 실행 환경, Ollama, `qwen3:0.6b` 모델 및 수정 가능한 CampusBot 프로젝트 소스를 포함합니다.

채팅 실행을 위해 Python, Docker 또는 Ollama를 설치할 필요가 없습니다. API 키와 최초 실행 시 모델 다운로드도 필요하지 않습니다.

### 실행 방법

1. ZIP 전체를 압축 해제합니다. ZIP 미리 보기 창에서 직접 실행하지 마십시오.
2. 압축을 푼 폴더를 엽니다.
3. `Start CampusBot.cmd`를 더블 클릭합니다.
4. 명령 창에 CampusBot이 준비되었다는 메시지가 표시될 때까지 기다립니다.
5. 브라우저에서 `http://127.0.0.1:8000/`이 자동으로 열립니다.
6. CampusBot을 사용하는 동안 명령 창을 닫지 마십시오.
7. 사용이 끝나면 명령 창으로 돌아가 Enter를 눌러 로컬 서비스를 종료합니다.

실수로 시작 창을 닫은 경우 `Stop CampusBot.cmd`를 더블 클릭하여 백그라운드 서비스를 정리할 수 있습니다.

실행기는 프로젝트 진입점을 자동으로 선택합니다. `CampusBot\serve.py`가 있으면 `serve.py`를 실행하고, 없으면 `CampusBot\main.py`를 실행합니다. 따라서 시작 명령을 직접 수정하지 않고도 단일 파일 프로그램을 모듈식 서비스로 단계적으로 리팩터링할 수 있습니다.

Windows 보안 경고가 표시되면 ZIP 파일이 신뢰할 수 있는 수업 배포 위치에서 제공되었는지 먼저 확인하십시오. 필요한 경우 More info를 선택한 다음 Run anyway를 선택하십시오. Ollama와 Python 실행 파일은 공식 배포본에서 가져왔지만, 이 결합 패키지에는 별도로 구매한 Windows 코드 서명 인증서가 없습니다.

수정 가능한 프로젝트 파일은 `CampusBot` 폴더에 있습니다. `main.py`, `prompt.txt`, `knowledge.json` 또는 `web` 아래의 파일을 변경한 뒤 CampusBot을 종료하고 다시 시작하면 변경 사항이 반영됩니다.

프로젝트에 `app`, `skills`, `governance`, `tests`, `config` 등의 디렉터리를 추가하여 스킬 라우팅, 신원 및 권한, 안전 규칙, 감사 로그, 대화 상태 및 자동 테스트를 구현할 수 있습니다.

테스트하려면 `CampusBot\tests` 아래에 `test_*.py` 파일을 추가한 뒤 `Run Tests.cmd`를 더블 클릭합니다. 테스트는 포함된 Python의 `unittest`를 사용하며 Ollama를 실행할 필요가 없습니다.

현재 실행 의존성은 이미 설치되어 있으며 오프라인 wheel 파일은 `runtime\wheels`에 있습니다. `requirements.txt`를 변경한 뒤 `Install Offline Dependencies.cmd`를 더블 클릭할 수 있습니다. 패키지에 없는 새 서드파티 라이브러리를 추가하려면 Windows x64 Python 3.11용 `.whl` 파일과 그 의존성 wheel을 `runtime\wheels`에 넣은 뒤 해당 명령을 실행하십시오.

로그 위치:

```text
%LOCALAPPDATA%\CampusBot Offline\logs\
```

시스템 요구 사항: 64비트 Windows 10/11, 8 GB 이상의 메모리 권장, 압축 해제를 위한 약 2 GB의 여유 공간. 모델 추론은 로컬에서 실행되며 첫 응답에는 시간이 더 걸릴 수 있습니다. 폭넓은 호환성과 더 작은 패키지를 위해 CPU 실행 구성 요소는 포함하지만 대용량 NVIDIA CUDA 가속 라이브러리는 제외했습니다.
