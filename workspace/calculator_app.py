"""
Module to generate the calculator web application files (HTML, CSS, JS)
and provide a Python-based wrapper/demonstration.
"""

import json

HTML_CONTENT = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Modern Calculator</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <div class="calculator">
        <div id="display" class="display">0</div>
        <div class="buttons">
            <button class="btn function" id="clear">C</button>
            <button class="btn function" id="sign">+/-</button>
            <button class="btn function" id="percent">%</button>
            <button class="btn operator" data-op="/">÷</button>
            
            <button class="btn number" data-num="7">7</button>
            <button class="btn number" data-num="8">8</button>
            <button class="btn number" data-num="9">9</button>
            <button class="btn operator" data-op="*">×</button>
            
            <button class="btn number" data-num="4">4</button>
            <button class="btn number" data-num="5">5</button>
            <button class="btn number" data-num="6">6</button>
            <button class="btn operator" data-op="-">-</button>
            
            <button class="btn number" data-num="1">1</button>
            <button class="btn number" data-num="2">2</button>
            <button class="btn number" data-num="3">3</button>
            <button class="btn operator" data-op="+">+</button>
            
            <button class="btn number zero" data-num="0">0</button>
            <button class="btn number" data-num=".">.</button>
            <button class="btn equals" id="equals">=</button>
        </div>
    </div>
    <script src="script.js"></script>
</body>
</html>
"""

CSS_CONTENT = """*
{
    box-sizing: border-box;
    margin: 0;
    padding: 0;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

body {
    display: flex;
    justify-content: center;
    align-items: center;
    height: 100vh;
    background: linear-gradient(135deg, #f5f7fa, #c3cfe2);
}

.calculator {
    background: #333;
    border-radius: 16px;
    box-shadow: 0 10px 25px rgba(0, 0, 0, 0.3);
    width: 320px;
    overflow: hidden;
}

.display {
    background: #222;
    color: #fff;
    font-size: 2.5rem;
    text-align: right;
    padding: 20px;
    word-wrap: break-word;
    word-break: break-all;
    min-height: 90px;
    display: flex;
    align-items: flex-end;
    justify-content: flex-end;
}

.buttons {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 1px;
    background: #444;
}

.btn {
    border: none;
    outline: none;
    padding: 20px;
    font-size: 1.25rem;
    cursor: pointer;
    background: #e0e0e0;
    color: #333;
    transition: background 0.2s;
}

.btn:hover {
    background: #d4d4d4;
}

.btn:active {
    background: #c0c0c0;
}

.btn.operator {
    background: #ff9500;
    color: #fff;
}

.btn.operator:hover {
    background: #e08500;
}

.btn.function {
    background: #d4d4d2;
}

.btn.function:hover {
    background: #b5b5b3;
}

.btn.equals {
    background: #ff9500;
    color: #fff;
}

.btn.equals:hover {
    background: #e08500;
}

.btn.zero {
    grid-column: span 2;
}
"""

JS_CONTENT = """// Core calculator logic and state management
class Calculator {
    constructor(displayElement) {
        this.displayElement = displayElement;
        this.clear();
    }

    clear() {
        this.currentInput = '0';
        this.previousInput = '';
        this.operation = null;
        this.resetNextInput = false;
    }

    appendNumber(number) {
        if (this.resetNextInput) {
            this.currentInput = '';
            this.resetNextInput = false;
        }
        if (number === '.' && this.currentInput.includes('.')) return;
        if (this.currentInput === '0' && number !== '.') {
            this.currentInput = number;
        } else {
            this.currentInput += number;
        }
    }

    chooseOperation(operation) {
        if (this.currentInput === '') return;
        if (this.previousInput !== '') {
            this.compute();
        }
        this.operation = operation;
        this.previousInput = this.currentInput;
        this.resetNextInput = true;
    }

    compute() {
        let computation;
        const prev = parseFloat(this.previousInput);
        const current = parseFloat(this.currentInput);
        if (isNaN(prev) || isNaN(current)) return;

        switch (this.operation) {
            case '+':
                computation = prev + current;
                break;
            case '-':
                computation = prev - current;
                break;
            case '*':
                computation = prev * current;
                break;
            case '/':
                computation = current === 0 ? 'Error' : prev / current;
                break;
            default:
                return;
        }

        this.currentInput = computation.toString();
        this.operation = null;
        this.previousInput = '';
        this.resetNextInput = true;
    }

    toggleSign() {
        if (this.currentInput === '0' || this.currentInput === 'Error') return;
        this.currentInput = (parseFloat(this.currentInput) * -1).toString();
    }

    percentage() {
        if (this.currentInput === 'Error') return;
        this.currentInput = (parseFloat(this.currentInput) / 100).toString();
    }

    updateDisplay() {
        this.displayElement.innerText = this.currentInput;
    }
}

// DOM Binding (executed when in browser environment)
document.addEventListener('DOMContentLoaded', () => {
    const display = document.getElementById('display');
    const calculator = new Calculator(display);

    document.querySelectorAll('.btn.number').forEach(button => {
        button.addEventListener('click', () => {
            calculator.appendNumber(button.getAttribute('data-num'));
            calculator.updateDisplay();
        });
    });

    document.querySelectorAll('.btn.operator').forEach(button => {
        button.addEventListener('click', () => {
            calculator.chooseOperation(button.getAttribute('data-op'));
            calculator.updateDisplay();
        });
    });

    document.getElementById('equals').addEventListener('click', () => {
        calculator.compute();
        calculator.updateDisplay();
    });

    document.getElementById('clear').addEventListener('click', () => {
        calculator.clear();
        calculator.updateDisplay();
    });

    document.getElementById('sign').addEventListener('click', () => {
        calculator.toggleSign();
        calculator.updateDisplay();
    });

    document.getElementById('percent').addEventListener('click', () => {
        calculator.percentage();
        calculator.updateDisplay();
    });
});
"""

class CalculatorBackend:
    """Python equivalent/helper for backend testing or demonstration of calculator logic."""
    @staticmethod
    def add(a, b):
        return a + b

    @staticmethod
    def subtract(a, b):
        return a - b

    @staticmethod
    def multiply(a, b):
        return a * b

    @staticmethod
    def divide(a, b):
        if b == 0:
            raise ValueError("Division by zero")
        return a / b

if __name__ == "__main__":
    print("Generating Calculator Web App files...")
    with open("index.html", "w") as f:
        f.write(HTML_CONTENT)
    with open("style.css", "w") as f:
        f.write(CSS_CONTENT)
    with open("script.js", "w") as f:
        f.write(JS_CONTENT)
    print("Successfully generated index.html, style.css, and script.js!")
