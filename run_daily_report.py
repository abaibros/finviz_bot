"""
run_daily_report.py
통합 실행 파일: 일일 매수 사냥개 리포트
"""

import os
import sys
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Tuple

import requests
from dotenv import load_dotenv

try:
    from zoneinfo import ZoneInfo
except ImportError:
    print("❌ Python 3.9+ 필요: zoneinfo 없음")
    sys.exit(1)


# ==================== 설정 ====================

BASE_DIR = Path(__file__).resolve().parent
KST = ZoneInfo("Asia/Seoul")

PIPELINE = [
    ("finviz_parser.py", "모듈 1: Finviz 추출"),
    ("yfinance_validator.py", "모듈 2: yfinance 검증"),
    ("scorer.py", "모듈 3: 점수화"),
    ("telegram_reporter.py", "모듈 4: 텔레그램 발송"),
]

STEP_TIMEOUT = 600


# ==================== 환경 변수 ====================

def load_credentials() -> Tuple[str, str]:
    load_dotenv(BASE_DIR / ".env")

    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")

    if not token or not chat_id:
        print("❌ TELEGRAM_BOT_TOKEN 또는 TELEGRAM_CHAT_ID 없음")
        sys.exit(1)

    return token, chat_id


# ==================== 텔레그램 에러 알림 ====================

def send_error_alert(token: str, chat_id: str, step_name: str, error_msg: str) -> None:
    now_kst = datetime.now(KST).strftime("%Y-%m-%d %H:%M")

    if len(error_msg) > 1500:
        error_msg = error_msg[:1500] + "\n... (잘림)"

    message = (
        f"⚠️ 매수 사냥개 봇 에러\n"
        f"시간: {now_kst} KST\n\n"
        f"실패 단계: {step_name}\n\n"
        f"에러 메시지:\n{error_msg}\n\n"
        f"조치: GitHub Actions 로그 확인 필요"
    )

    try:
        r = requests.post(
            f"https://api.telegram.org/bot{token}/sendMessage",
            data={"chat_id": chat_id, "text": message},
            timeout=10,
        )

        if r.status_code == 200:
            print("✅ 텔레그램 에러 알림 발송 완료")
        else:
            print(f"⚠️ 텔레그램 알림 실패: {r.status_code} / {r.text[:300]}")

    except Exception as e:
        print(f"⚠️ 텔레그램 알림 예외: {type(e).__name__}: {e}")


# ==================== 단계 실행 ====================

def run_step(script_name: str, step_name: str) -> Tuple[bool, str]:
    script_path = BASE_DIR / script_name

    print("\n" + "=" * 60)
    print(f"▶ {step_name} 시작")
    print(f"실행 파일: {script_path}")
    print("=" * 60)

    if not script_path.exists():
        return False, f"스크립트 파일 없음: {script_path}"

    try:
        result = subprocess.run(
            [sys.executable, str(script_path)],
            cwd=BASE_DIR,
            capture_output=True,
            text=True,
            timeout=STEP_TIMEOUT,
            encoding="utf-8",
            errors="replace",
        )

        if result.stdout:
            print(result.stdout)

        if result.stderr:
            print("[stderr]")
            print(result.stderr)

        if result.returncode == 0:
            print(f"✅ {step_name} 완료")
            return True, ""

        error_msg = (
            f"종료 코드: {result.returncode}\n"
            f"stderr:\n{result.stderr[-1500:] if result.stderr else 'stderr 없음'}\n"
            f"stdout:\n{result.stdout[-1000:] if result.stdout else 'stdout 없음'}"
        )

        return False, error_msg

    except subprocess.TimeoutExpired:
        return False, f"타임아웃: {STEP_TIMEOUT}초 초과"

    except Exception as e:
        return False, f"{type(e).__name__}: {e}"


# ==================== 메인 ====================

def main() -> int:
    start_time = datetime.now(KST)

    print("=" * 60)
    print("🎯 매수 사냥개 일일 리포트 시작")
    print(f"시작 시각: {start_time.strftime('%Y-%m-%d %H:%M:%S')} KST")
    print("=" * 60)

    token, chat_id = load_credentials()

    for script_name, step_name in PIPELINE:
        success, error_msg = run_step(script_name, step_name)

        if not success:
            print("\n" + "=" * 60)
            print(f"❌ 파이프라인 중단: {step_name}")
            print(error_msg)
            print("=" * 60)

            send_error_alert(token, chat_id, step_name, error_msg)
            return 1

    end_time = datetime.now(KST)
    duration = (end_time - start_time).total_seconds()

    print("\n" + "=" * 60)
    print("🎉 매수 사냥개 일일 리포트 완료")
    print(f"종료 시각: {end_time.strftime('%Y-%m-%d %H:%M:%S')} KST")
    print(f"총 소요 시간: {duration:.1f}초")
    print("=" * 60)

    return 0


if __name__ == "__main__":
    sys.exit(main())