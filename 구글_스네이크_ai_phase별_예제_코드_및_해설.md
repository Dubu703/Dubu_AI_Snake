# 구글 스네이크 AI – Phase별 학습 통합 문서

본 문서는 **이전 파일의 코드 역할·설계 해설**과 **현재 파일의 라이브러리·함수 설명**을 완전히 융합한 학습용 통합 문서이다.

목표는 다음과 같다:
- 학습자가 TODO 리스트를 따라가며 **왜 이 Phase가 필요한지** 이해
- 각 코드가 **AI 시스템에서 맡는 책임(Responsibility)** 명확화
- 파이썬 문법이 아니라 **AI 설계 사고 구조** 학습

각 Phase는 동일한 구조로 설명된다.

1. Phase의 학습 목적 (TODO와 연결)
2. AI 시스템에서의 역할
3. 예제 코드
4. 사용 라이브러리·함수 설명
5. 코드가 의미하는 AI 설계 개념
6. 이 Phase가 없을 때 발생하는 문제

---

## Phase 1. 문제 정의 및 행동 공간 설계

### 1️⃣ 학습 목적 (TODO 연결)
- AI가 선택할 수 있는 행동의 범위를 명확히 정의한다
- 행동 공간(Action Space) 개념을 이해한다

### 2️⃣ 시스템에서의 역할
- **AI 의사결정의 가장 바깥 경계**를 정의
- 잘못된 행동 선택 자체를 구조적으로 차단

### 3️⃣ 예제 코드
```python
from enum import Enum

class Direction(Enum):
    UP = (0, -1)
    DOWN = (0, 1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)
```

### 4️⃣ 사용 라이브러리·함수 설명

#### enum.Enum
- 유한한 상수 집합 정의
- 행동 공간을 수학적으로 닫힌 집합으로 만듦

### 5️⃣ AI 설계 개념
- 행동 공간 정의는 강화학습, 탐색, 최적화 모든 AI의 출발점

### 6️⃣ 이 Phase가 없으면?
- AI는 임의의 값도 행동으로 선택 가능
- 정책(policy) 개념이 성립하지 않음

---

## Phase 2. 환경(Environment) 시뮬레이션 구축

### 1️⃣ 학습 목적
- AI와 세계를 분리하는 구조를 이해
- 시뮬레이션 반복 가능성 확보

### 2️⃣ 시스템 역할
- 게임 규칙을 **객체 하나로 캡슐화**
- AI는 환경 내부를 직접 수정하지 않음

### 3️⃣ 예제 코드
```python
from collections import deque

class SnakeEnv:
    def __init__(self, size=10):
        self.size = size
        self.snake = deque([(5, 5), (5, 6)])
        self.direction = Direction.UP
        self.food = (2, 2)

    def step(self, action_dir):
        head_x, head_y = self.snake[0]
        dx, dy = action_dir.value
        new_head = (head_x + dx, head_y + dy)
        self.snake.appendleft(new_head)
        self.snake.pop()
```

### 4️⃣ 라이브러리·함수

#### collections.deque
- 머리/꼬리 이동을 O(1)로 처리
- 스네이크 물리 구조와 정확히 대응

### 5️⃣ AI 설계 개념
- 환경은 상태 전이 함수(State Transition Function)

### 6️⃣ 이 Phase가 없으면?
- 규칙과 AI 로직이 뒤섞여 확장 불가

---

## Phase 3. 상태(State) 인식 및 표현

### 1️⃣ 학습 목적
- 세계를 수학적 데이터로 변환

### 2️⃣ 시스템 역할
- 감각 기관 역할 (Perception Layer)

### 3️⃣ 예제 코드
```python
import numpy as np

def encode_board(size, snake, food):
    board = np.zeros((size, size), dtype=int)
    for x, y in snake:
        board[y][x] = 1
    fx, fy = food
    board[fy][fx] = 2
    return board
```

### 4️⃣ 라이브러리·함수

#### numpy.zeros
- 상태를 행렬로 표현
- 추후 딥러닝으로 확장 가능

### 5️⃣ AI 설계 개념
- 상태 공간(State Space) 정의

### 6️⃣ 이 Phase가 없으면?
- AI는 세계를 비교·학습 불가

---

## Phase 4. 생존 제약 조건 판단

### 1️⃣ 학습 목적
- 보상 이전에 "죽지 않는" 규칙 이해

### 2️⃣ 시스템 역할
- 하드 제약(Hard Constraint) 처리

### 3️⃣ 예제 코드
```python
def is_collision(pos, size, snake):
    x, y = pos
    if x < 0 or x >= size or y < 0 or y >= size:
        return True
    if pos in snake:
        return True
    return False
```

### 4️⃣ 함수 설명
- 충돌 여부 즉시 판단

### 5️⃣ AI 설계 개념
- 제약 만족 문제(CSP)

### 6️⃣ 이 Phase가 없으면?
- 고득점 이전에 즉시 게임 오버

---

## Phase 5. 경로 계획 (Path Planning)

### 1️⃣ 학습 목적
- 목표 지향적 행동 설계

### 2️⃣ 시스템 역할
- 음식까지의 안전한 경로 탐색

### 3️⃣ 예제 코드
```python
def heuristic(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])
```

### 4️⃣ 함수·라이브러리
- abs: 거리 계산

### 5️⃣ AI 설계 개념
- A* 휴리스틱

### 6️⃣ 이 Phase가 없으면?
- AI는 근시안적 행동만 수행

---

## Phase 6. 비용 함수 및 회전 최소화

### 1️⃣ 학습 목적
- 다중 목표 최적화 이해

### 2️⃣ 시스템 역할
- 행동 품질 정량화

### 3️⃣ 예제 코드
```python
def turn_cost(current_dir, next_dir):
    return 0 if current_dir == next_dir else 1
```

### 4️⃣ 함수 설명
- 방향 변경 비용 계산

### 5️⃣ AI 설계 개념
- Cost Function 설계

### 6️⃣ 이 Phase가 없으면?
- 불필요한 회전 증가

---

## Phase 7. 정책(Policy) 선택

### 1️⃣ 학습 목적
- 의사결정 규칙 명확화

### 2️⃣ 시스템 역할
- 최종 행동 결정

### 3️⃣ 예제 코드
```python
def choose_action(actions):
    safe_actions = [a for a in actions if not a['unsafe']]
    return min(safe_actions, key=lambda a: a['cost'])
```

### 4️⃣ 사용 문법
- 리스트 컴프리헨션, min

### 5️⃣ AI 설계 개념
- 정책 함수

### 6️⃣ 이 Phase가 없으면?
- 평가만 있고 실행 불가

---

## Phase 8. 평가 및 실험 로그

### 1️⃣ 학습 목적
- AI 성능을 수치로 이해

### 2️⃣ 시스템 역할
- 실험 결과 기록

### 3️⃣ 예제 코드
```python
log = {
    'score': [],
    'turns': [],
}
```

### 4️⃣ 자료구조 설명
- dict + list

### 5️⃣ AI 설계 개념
- 실험 기반 개선

### 6️⃣ 이 Phase가 없으면?
- 개선 방향 상실

---

## Phase 9. 확장 가능한 정책 구조

### 1️⃣ 학습 목적
- 규칙 기반 → 학습 기반 전환 준비

### 2️⃣ 시스템 역할
- 정책 인터페이스

### 3️⃣ 예제 코드
```python
class Policy:
    def act(self, state):
        raise NotImplementedError
```

### 4️⃣ 설계 패턴
- 추상화

### 5️⃣ AI 설계 개념
- 알고리즘 교체 가능 구조

### 6️⃣ 이 Phase가 없으면?
- 확장 불가능한 AI

---

## 최종 학습 요약

이 문서는 TODO 리스트 → Phase → 코드 → AI 개념이 **선형적으로 연결**되도록 설계되었다.

> 학습자는 이 문서를 통해 "코드를 치는 사람"이 아니라
> **AI 시스템을 설계하는 사람의 사고 흐름**을 학습하게 된다.

