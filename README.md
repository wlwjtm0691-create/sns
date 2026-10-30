# 블로그 편집실 시작하기

주제만 입력하면 Codex가 리서치부터 검수 기록과 최종 원고 저장까지 진행하도록 구성되어 있습니다.

## 글 한 편의 파일
각 글은 posts/YYYY-MM-DD-slug/에 다음 파일로 저장합니다.

- brief.md: 주제 해석, 독자, 핵심 질문, 범위
- research.md: 주장별 근거와 원문 링크, 발행일·확인일
- draft.md: 검수와 수정을 마친 원고
- review.md: 확인한 출처와 검수 체크리스트
- final.md: 검증 스크립트가 생성한 최종 원고

## 최종 원고 만들기
검수 항목을 모두 확인하고 review.md에서 [x]로 표시한 뒤 아래 명령을 실행합니다.

python scripts/validate_article.py "posts/YYYY-MM-DD-slug" --promote
python scripts/validate_article.py "posts/YYYY-MM-DD-slug"

첫 명령은 필수 파일, 출처 링크, 임시 문구, 검수 체크리스트를 검사한 뒤 draft.md를 final.md로 새로 저장합니다. 기존 final.md는 덮어쓰지 않습니다. 둘째 명령은 저장된 최종 원고를 다시 검사합니다.

자동 검사는 구조와 필수 표시를 검사합니다. 출처가 주장을 실제로 뒷받침하는지, 내용이 정확한지는 원문을 확인하고 검수 기록에 남겨야 합니다.
