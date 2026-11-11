"""Offline SEO/GEO planning; no invented traffic or search rankings."""
def plan(topic, country, visa_type):
    if not all((topic, country, visa_type)):
        raise ValueError('topic, country and visa_type are required')
    return {
        'topic': topic, 'country': country, 'visa_type': visa_type,
        'search_intents_to_validate': ['必要書類', '申請費用', '申請手順', '制度変更', 'よくある質問'],
        'article_sections': ['結論', '対象者', '必要書類', '手順', '費用', 'FAQ', '公式情報'],
        'geo_requirements': ['冒頭で質問に直接回答', '対象国・制度・確認日を明記', '主張ごとに一次情報', '専門用語を平易に説明'],
        'search_console_metrics': 'NOT_CONNECTED',
        'rankings': 'NOT_MEASURED',
        'competitor_analysis': 'NOT_RUN',
    }
