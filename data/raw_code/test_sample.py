import os
import sys

# 이것은 Orphan(고아) 코드로 분류되어야 합니다.
GLOBAL_SETTINGS = {
    "version": "1.0",
    "status": "testing"
}

def standalone_function():
    print("이것은 독립된 함수입니다.")

class Calculator:
    def __init__(self):
        self.value = 0
        
    def add(self, a, b):
        return a + b
