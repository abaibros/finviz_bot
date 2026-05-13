"""
모듈 0: 텔레그램 전송 테스트
목적: 봇 토큰·채팅 ID 작동 확인
"""

import os
import sys
import requests
from dotenv import load_dotenv


def load_credentials():
    load_dotenv()

    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")

    if not token:
        print("ERROR: TELEGRAM_BOT_TOKEN이 .env 파일에 없습니다.")
        print(".env 파일을 확인하세요.")
        sys.exit(1)

    if not chat_id:
        print("ERROR: TELEGRAM_CHAT_ID가 .env 파일에 없습니다.")
        print(".env 파일을 확인하세요.")
        sys.exit(1)

    print(".env 파일에서 인증 정보 로드 성공")
    return token, chat_id


def send_telegram_message(token: str, chat_id: str, message: str) -> bool:
    url = f"https://api.telegram.org/bot{token}/sendMessage"

    payload = {
        "chat_id": chat_id,
        "text": message,
    }

    try:
        print("텔레그램 메시지 전송 시도...")
        response = requests.post(url, data=payload, timeout=10)

        if response.status_code == 200:
            print(f"전송 성공. status: {response.status_code}")
            return True
        else:
            print(f"전송 실패. status: {response.status_code}")
            print(f"응답: {response.text}")
            return False

    except requests.exceptions.Timeout:
        print("ERROR: 텔레그램 서버 응답 타임아웃")
        return False

    except requests.exceptions.RequestException as e:
        print(f"ERROR: 네트워크 요청 실패 - {e}")
        return False


def main():
    print("=" * 50)
    print("모듈 0: 텔레그램 전송 테스트")
    print("=" * 50)

    token, chat_id = load_credentials()

    test_message = "Finviz MVP Telegram test success"
    success = send_telegram_message(token, chat_id, test_message)

    print("=" * 50)
    if success:
        print("모듈 0 테스트 성공")
        print("본인 텔레그램에서 메시지 확인하세요.")
    else:
        print("모듈 0 테스트 실패")
        print(".env 파일, 토큰, Chat ID를 다시 확인하세요.")
    print("=" * 50)


if __name__ == "__main__":
    main()