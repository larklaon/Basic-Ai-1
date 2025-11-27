import cv2

def display_image(image_path):
    """이미지 파일을 읽어서 화면에 출력하는 함수"""
    # 이미지 파일 읽기
    image = cv2.imread(image_path)
    
    # 이미지 읽기 실패 시 처리
    if image is None:
        print(f'이미지를 불러올 수 없습니다: {image_path}')
        return
    
    # 이미지 출력
    cv2.imshow('Image Display', image)
    
    # 33ms 동안 키 입력 대기
    # cv2.waitKey(33)

    cv2.waitKey(0)


# 실행 예제
if __name__ == '__main__':
    # 이미지 파일 경로를 입력하세요
    image_path = '2.png'
    display_image(image_path)
