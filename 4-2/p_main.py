import pandas as pd
import matplotlib.pyplot as plt
import platform


def load_csv_data(file_path):
    """CSV 파일을 DataFrame으로 읽어들이는 함수"""
    try:
        df = pd.read_csv(file_path, encoding='utf-8')
    except UnicodeDecodeError:
        df = pd.read_csv(file_path, encoding='cp949')
    
    return df


def filter_columns(df):
    """일반가구원 관련 컬럼만 남기고 나머지 삭제"""
    # 분석에 필요한 컬럼만 유지
    columns_to_keep = ['시점', '성별', '연령별', '일반가구원']
    df_filtered = df[columns_to_keep]
    
    return df_filtered


def filter_by_year(df, start_year=2015):
    """2015년 이후 데이터만 필터링"""
    # 시점 컬럼을 정수로 변환
    df['시점'] = df['시점'].astype(int)
    df_filtered = df[df['시점'] >= start_year]
    
    return df_filtered


def filter_gender_data(df):
    """남자와 여자 데이터만 필터링 (계 제외)"""
    df_filtered = df[df['성별'].isin(['남자', '여자'])]
    
    return df_filtered


def get_gender_statistics(df):
    """남자 및 여자의 연도별 일반가구원 데이터 통계"""
    # 성별, 연도별 그룹화
    gender_stats = df.groupby(['시점', '성별'])['일반가구원'].sum().reset_index()
    
    print('=== 남자 및 여자의 연도별 일반가구원 통계 ===')
    print(gender_stats)
    print()
    
    return gender_stats


def get_age_statistics(df):
    """연령별 일반가구원 데이터 통계"""
    # '합계'를 제외한 연령별 데이터
    df_age = df[df['연령별'] != '합계']
    
    # 연령별 그룹화
    age_stats = df_age.groupby('연령별')['일반가구원'].sum().reset_index()
    
    print('=== 연령별 일반가구원 통계 ===')
    print(age_stats)
    print()
    
    return age_stats


def get_gender_age_statistics(df):
    """남자 및 여자의 연령별 일반가구원 데이터 통계"""
    # '합계'를 제외한 데이터
    df_filtered = df[df['연령별'] != '합계']
    
    # 성별, 연령별 그룹화
    gender_age_stats = df_filtered.groupby(['성별', '연령별'])['일반가구원'].sum().reset_index()
    
    print('=== 남자 및 여자의 연령별 일반가구원 통계 ===')
    print(gender_age_stats)
    print()
    
    return gender_age_stats


def plot_gender_age_graph(df):
    """남자 및 여자의 연령별 일반가구원 데이터를 꺾은선 그래프로 표현"""
    # 한글 폰트 설정
    if platform.system() == 'Darwin':
        plt.rc('font', family='AppleGothic')
    elif platform.system() == 'Windows':
        plt.rc('font', family='Malgun Gothic')
    
    plt.rc('axes', unicode_minus=False)
    
    # '합계', '15~64세' 등 집계 구간 제외
    exclude_ages = ['합계', '15~64세', '15세미만']
    df_filtered = df[~df['연령별'].isin(exclude_ages)]
    
    # 성별로 데이터 분리
    male_data = df_filtered[df_filtered['성별'] == '남자'].groupby('연령별')['일반가구원'].sum()
    female_data = df_filtered[df_filtered['성별'] == '여자'].groupby('연령별')['일반가구원'].sum()
    
    # 그래프 설정
    fig, ax = plt.subplots(figsize=(14, 7))
    ax.plot(male_data.index, male_data.values, marker='o', label='남자', linewidth=2)
    ax.plot(female_data.index, female_data.values, marker='s', label='여자', linewidth=2)
    
    # Y축을 일반 숫자 형식으로 표시
    ax.ticklabel_format(style='plain', axis='y')
    
    # 또는 천 단위 구분 쉼표 추가
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: format(int(x), ',')))
    
    ax.set_title('연령별 일반가구원 통계 (남자 vs 여자)', fontsize=14, fontweight='bold')
    ax.set_xlabel('연령', fontsize=12)
    ax.set_ylabel('일반가구원 수', fontsize=12)
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3)
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.show()


def main():
    """메인 실행 함수"""
    # 1. CSV 파일 읽기
    file_path = 'census.csv'
    df = load_csv_data(file_path)
    
    # 2. 일반가구원 컬럼만 남기기
    df = filter_columns(df)
    
    # 3. 2015년 이후 데이터 필터링
    df = filter_by_year(df, start_year=2015)
    
    # 4. 남자와 여자 데이터만 필터링
    df_gender = filter_gender_data(df)
    
    # 5. 남자 및 여자의 연도별 통계
    gender_stats = get_gender_statistics(df_gender)
    
    # 6. 연령별 통계
    age_stats = get_age_statistics(df_gender)
    
    # 7. 남자 및 여자의 연령별 통계
    gender_age_stats = get_gender_age_statistics(df_gender)
    
    # 8. 꺾은선 그래프 출력
    plot_gender_age_graph(df_gender)


if __name__ == '__main__':
    main()
