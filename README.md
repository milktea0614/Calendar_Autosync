# Calendar_Autosync
Autosync the specific site information into calendar.

**History**: https://milktea0614.tistory.com/79

&nbsp;

Able site: [Job-Alio](https://job.alio.go.kr/recruit.do)

Able calendar: Naver calendar Mobile App.

&nbsp;

---
## Result
<details>
<summary><b>Show run_jobalio_naver.py result.</b></summary>
<br>
<img src="_result/2023-09-15 12-26-53_run_jobalio_naver.gif" alt="run_jobalio_naver.py result">
<br>
</details>

---
## Mobile configuration information

Refer to https://appium.io/docs/en/2.1/guides/caps/

---

## Web scraping configuration information

### Fixed values

- **eduType**: Option for '학력 옵션' is fixed as 'multi'.
- **replacement**: Option for '대체인력유무' is not selected.
- **org_type**: Option for '기관유형' is not selected.
- **ing**: Option for '상태' is not selected

### detail_code
Code for selecting the '채용분야'. (Optional, Multi-selectable)
<details>
<summary>Show the detail_code list</summary>

- 600001 = 산업관리 
- 600002 = 경영·회계·사무 
- 600003 = 금융·보험 
- 600004 = 교육·자연·사회과학 
- 600005 = 법률·경찰·소방·교도·국방 
- 600006 = 보건·의료 
- 600007 = 사회복지·종교 
- 600008 = 문화·예술·디자인·방송 
- 600009 = 운전·운송 
- 600010 = 영업판매 
- 600011 = 경비·청소 
- 600012 = 이용·숙박·여행·오락·스포츠 
- 600013 = 음식서비스 
- 600014 = 건설 
- 600015 = 기계 
- 600016 = 재료 
- 600017 = 화학
- 600018 = 섬유·의복 
- 600019 = 전기·전자 
- 600020 = 정보통신 
- 600021 = 식품가공 
- 600022 = 인쇄·목재·가구·공예 
- 600023 = 환경·에너지·안전 
- 600024 = 농림어업 
- 600025 = 연구

</details>

### location
Code for selecting the '위치'. (Optional, Multi-selectable)
<details>
<summary><b>Show the location list</b></summary>

- R3009 = 해외 
- R3010 = 서울특별시
- R3011 = 인천광역시
- R3012 = 대전광역시
- R3013 = 대구광역시
- R3014 = 부산광역시
- R3015 = 광주광역시
- R3016 = 울산광역시
- R3017 = 경기도
- R3018 = 강원도
- R3019 = 충청남도
- R3020 = 충청북도
- R3021 = 경상북도
- R3022 = 경상남도
- R3023 = 전라남도
- R3024 = 전라북도
- R3025 = 제주특별자치도
- R3026 = 세종특별자치시

</details>

### work_type
Code for selecting the '고용형태'. (Optional, Multi-selectable)
<details>
<summary><b>Show the work_type list</b></summary>

- R1010 = 정규직
- R1030 = 무기계약직
- R1040 = 비정규직
- R1060 = 청년인턴(체험형)
- R1070 = 청년인턴(채용형)

</details>

### career
Code for selecting the '채용 구분'. (Optional, Multi-selectable)
<details>
<summary><b>Show the career list</b></summary>

- R2010 = 신입
- R2020 = 경력
- R2030 = 신입+경력
- R2040 = 외국인 전형

</details>

### education
Code for selecting the '학력 정보'. (Optional, Multi-selectable)
<details>
<summary><b>Show the career list</b></summary>

- R7010 = 학력무관
- R7020 = 중졸이하
- R7030 = 고졸
- R7040 = 대졸(2~3년)
- R7050 = 대졸(4년)
- R7060 = 석사
- R7070 = 박사

</details>

---
