// Core calculator logic and state management
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
