import pandas as pd
import matplotlib.pyplot as plt


# MacOS 한글 폰트 설정
plt.rcParams['font.family'] = 'AppleGothic'
plt.rcParams['axes.unicode_minus'] = False


def print_basic_info(df, name):
    '''데이터프레임 기본 정보를 출력한다.'''
    print(f'\n[{name}] 데이터 정보')
    print(f'총 행 수: {len(df)}')
    print(f'총 열 수: {len(df.columns)}')
    print('\n열별 정보:')
    for col in df.columns:
        non_null_count = df[col].notna().sum()
        unique_count = df[col].nunique(dropna=True)
        print(f'- {col}: 유효한 값={non_null_count}, 고유값={unique_count}')


def classify_age_group(age):
    '''나이를 연령대로 분류한다.'''
    if pd.isna(age):
        return None
    if age < 20:
        return '10대'
    if age < 30:
        return '20대'
    if age < 40:
        return '30대'
    if age < 50:
        return '40대'
    if age < 60:
        return '50대'
    if age < 70:
        return '60대'
    return '70대 이상'


def convert_boolean_column(series):
    '''불리언 컬럼을 안전하게 0/1로 변환한다.'''
    if series.dtype == 'object':
        result = series.map({'True': 1, 'False': 0, True: 1, False: 0})
    elif series.dtype == 'bool':
        result = series.astype(int)
    else:
        result = series
    return result.fillna(0).astype(int)


def prepare_correlation_data(data):
    '''상관계수 계산을 위한 데이터 전처리 후 숫자형 데이터프레임을 반환한다.'''
    corr_data = data[data['Transported'].notna()].copy()

    # Transported를 정수(1/0)로 변환
    corr_data['Transported'] = convert_boolean_column(corr_data['Transported'])

    # 불리언 컬럼 -> 1/0
    boolean_columns = [col for col in ['CryoSleep', 'VIP'] if col in corr_data.columns]
    for col in boolean_columns:
        corr_data[col] = convert_boolean_column(corr_data[col])

    # 범주형 -> 정수 인코딩
    categorical_columns = [col for col in ['HomePlanet', 'Destination'] if col in corr_data.columns]
    for col in categorical_columns:
        unique_vals = corr_data[col].dropna().unique()
        mapping = {val: idx for idx, val in enumerate(unique_vals)}
        corr_data[col] = corr_data[col].map(mapping)

    # 숫자형 컬럼 선택
    candidate_columns = [
        'Age', 'RoomService', 'FoodCourt', 'ShoppingMall', 'Spa', 'VRDeck',
        'CryoSleep', 'VIP', 'HomePlanet', 'Destination', 'Transported'
    ]
    present_cols = [c for c in candidate_columns if c in corr_data.columns]

    # 각 컬럼의 결측값을 0으로 채움 (지출 항목은 0이 의미있음)
    for col in present_cols:
        if col in ['RoomService', 'FoodCourt', 'ShoppingMall', 'Spa', 'VRDeck']:
            corr_data[col] = corr_data[col].fillna(0)
        elif col == 'Age':
            corr_data[col] = corr_data[col].fillna(corr_data[col].median())

    # 여전히 NaN이 있는 행만 제거
    analysis_data = corr_data[present_cols].dropna()

    return analysis_data


def main():
    # 1) CSV 읽기
    train_data = pd.read_csv('train.csv')
    test_data = pd.read_csv('test.csv')

    # 2) 구조 확인
    print_basic_info(train_data, 'Train')
    print_basic_info(test_data, 'Test')

    # 3) 병합
    merged_data = pd.concat([train_data, test_data], ignore_index=True)
    
    # 병합된 데이터 정보 출력
    print_basic_info(merged_data, 'Merged')
    
    # 병합된 데이터를 CSV로 저장
    merged_data.to_csv('merged_data.csv', index=False, encoding='utf-8-sig')
    print('\n병합된 데이터를 merged_data.csv 파일로 저장했습니다.')

    # 4) 연령대 컬럼 생성
    merged_data['AgeGroup'] = merged_data['Age'].apply(classify_age_group)

    # 5) 연령대별 Transported 그래프 (Train 부분만 사용)
    train_only = merged_data[merged_data['Transported'].notna()].copy()
    age_df = train_only.dropna(subset=['AgeGroup'])
    if not age_df.empty:
        age_counts = age_df.groupby(['AgeGroup', 'Transported']).size().unstack(fill_value=0)

        age_order = ['10대', '20대', '30대', '40대', '50대', '60대', '70대 이상']
        age_counts = age_counts.reindex(age_order).fillna(0)
        age_counts = age_counts.reindex(columns=[False, True], fill_value=0).astype(int)

        # 시각화
        plot_df = age_counts.rename(columns={False: '전송되지 않음', True: '전송됨'})
        ax = plot_df.plot(kind='bar', figsize=(12, 6), color=['#FF6B6B', '#4ECDC4'], rot=0)
        ax.set_title('연령대별 Transported 여부', fontsize=16)
        ax.set_xlabel('연령대', fontsize=12)
        ax.set_ylabel('인원 수', fontsize=12)
        ax.legend(loc='upper right')
        plt.tight_layout()
        plt.savefig('age_transported.png', dpi=300)
        plt.show()

        # 연령대별 전송 비율 출력
        print('\n연령대별 전송 비율(%)')
        total_by_age = age_counts.sum(axis=1).replace(0, pd.NA)
        age_rate = (age_counts[True] / total_by_age * 100).round(2)
        for age_group, rate in age_rate.items():
            value = 'N/A' if pd.isna(rate) else f'{rate}%'
            print(f'- {age_group}: {value}')
    else:
        print('\n연령 정보가 없어 연령대별 그래프를 생성할 수 없습니다.')

    # 6) 상관계수 분석: Transported와 가장 관련성 높은 항목 찾기
    analysis_data = prepare_correlation_data(merged_data)
    
    print(f'\n상관계수 분석에 사용된 데이터 수: {len(analysis_data)}')
    
    if analysis_data.empty or len(analysis_data) < 2:
        print('\n상관계수 분석을 위한 유효한 숫자 데이터가 충분하지 않습니다.')
        return

    corr_mat = analysis_data.corr()
    transported_corr = corr_mat['Transported'].drop('Transported')

    # 절댓값 기준 내림차순 정렬
    transported_corr_sorted = transported_corr.reindex(transported_corr.abs().sort_values(ascending=False).index)

    print('\nTransported와의 상관계수 (절댓값 기준 내림차순):')
    for feature, value in transported_corr_sorted.items():
        print(f'- {feature}: {value:.4f}')

    # 상위 5개 시각화
    top_idx = list(transported_corr_sorted.index[:5])
    if top_idx:
        top_vals = [transported_corr[feat] for feat in top_idx]
        colors = ['#2E7D32' if v > 0 else '#C62828' for v in top_vals]

        fig, ax = plt.subplots(figsize=(10, 6))
        ax.barh(range(len(top_idx)), top_vals, color=colors)
        ax.set_yticks(range(len(top_idx)))
        ax.set_yticklabels(top_idx)
        ax.set_xlabel('상관계수', fontsize=12)
        ax.set_title('Transported와 상관관계 상위 5개 항목', fontsize=14)
        ax.axvline(x=0, color='black', linestyle='-', linewidth=0.5)
        plt.tight_layout()
        plt.savefig('correlation_top5.png', dpi=300)
        plt.show()

        print(f'\n가장 관련성이 높은 항목: {top_idx[0]}')
        print(f'상관계수: {transported_corr[top_idx[0]]:.4f}')
    else:
        print('\n상관계수를 계산할 항목이 없습니다.')


if __name__ == '__main__':
    main()
