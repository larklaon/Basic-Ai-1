import cv2
from datetime import datetime


def get_filename_with_timestamp():
    """현재 시간을 기반으로 파일명 생성"""
    now = datetime.now()
    return now.strftime('%Y%m%d_%H-%M-%S')


def video_player_with_controls(video_path):
    """단축키 기반 동영상 재생 및 제어 함수"""
    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        print(f'동영상을 열 수 없습니다: {video_path}')
        return

    fps = int(cap.get(cv2.CAP_PROP_FPS))
    if fps == 0:
        fps = 30  # FPS 정보가 없을 경우 기본값 설정

    is_recording = False
    video_writer = None

    print('동영상 재생 시작')
    print('ESC: 종료 | Ctrl+Z: 캡처 | Ctrl+X: 녹화 시작 | Ctrl+C: 녹화 중지')

    while True:
        ret, frame = cap.read()
        if not ret:
            print('동영상 재생 완료')
            break

        if is_recording and video_writer is not None:
            video_writer.write(frame)

        cv2.imshow('Video Player', frame)

        key = cv2.waitKey(33)

        # ESC: 종료
        if key == 27:
            print('프로그램 종료')
            break

        # Ctrl+Z: 캡처
        elif key == 26:
            filename = get_filename_with_timestamp() + '.jpg'
            cv2.imwrite(filename, frame)
            print(f'화면 캡처 완료: {filename}')

        # Ctrl+X: 녹화 시작
        elif key == 24:
            if not is_recording:
                filename = get_filename_with_timestamp() + '.mp4'
                fourcc = cv2.VideoWriter_fourcc(*'avc1')  # macOS 권장 코덱
                frame_height, frame_width = frame.shape[:2]
                video_writer = cv2.VideoWriter(filename, fourcc, fps, (frame_width, frame_height))
                is_recording = True
                print(f'녹화 시작: {filename}')
            else:
                print('이미 녹화 중입니다')

        # Ctrl+C: 녹화 중지
        elif key == 3:
            if is_recording:
                is_recording = False
                if video_writer is not None:
                    video_writer.release()
                    video_writer = None
                print('녹화 중지')
            else:
                print('녹화 중이 아닙니다')

    # 자동 저장하는 코드
    if video_writer is not None:
        video_writer.release()
    cap.release()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    video_path = '6.mp4'
    video_player_with_controls(video_path)
