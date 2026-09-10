import re
import sympy
from typing import Tuple, List, Optional
from backend.core.models import FactVerdict

class CalculatorAgent:
    """
    Step 4: Mathematical Verification Agent
    • Calculates expressions directly using exact symbolic evaluation.
    • Checks arithmetic, units, inequalities, and comparisons.
    • Handles:
      - '2 + 2 = 4' -> TRUE
      - '2 + 2 = 5' -> FALSE (Correct: 4)
      - '10 × 5 = 50' -> TRUE
      - '100 is less than 20' -> FALSE
      - '25% of 200 is 50' -> TRUE
    """

    SAFE_MATH_FUNCS = {
        "sqrt": sympy.sqrt,
        "pow": sympy.Pow,
        "sin": sympy.sin,
        "cos": sympy.cos,
        "tan": sympy.tan,
        "abs": sympy.Abs,
        "log": sympy.log,
        "pi": sympy.pi,
        "E": sympy.E
    }

    def sanitize(self, expr_str: str) -> str:
        s = expr_str.strip()
        # percentage of: '25% of 200' -> '(25/100)*200'
        s = re.sub(r'(\d+(?:\.\d+)?)\s*%\s*of\s*(\d+(?:\.\d+)?)', r'(\1/100)*\2', s, flags=re.IGNORECASE)
        # standalone percentage: '25%' -> '(25/100)'
        s = re.sub(r'(\d+(?:\.\d+)?)\s*%', r'(\1/100)', s)
        # caret to double asterisk
        s = s.replace('^', '**')
        # multiplication signs: '10 x 5' or '10 × 5'
        s = re.sub(r'(\d+)\s*[xX×]\s*(\d+)', r'\1 * \2', s)
        return s

    def evaluate_safe(self, expr_str: str) -> Tuple[Optional[sympy.Expr], Optional[str]]:
        try:
            sanitized = self.sanitize(expr_str)
            parsed = sympy.sympify(sanitized, locals=self.SAFE_MATH_FUNCS, evaluate=True)
            return parsed, None
        except Exception as e:
            return None, str(e)

    def verify_mathematical_claim(self, claim: str) -> Tuple[FactVerdict, int, str, List[str], Optional[str]]:
        """
        Returns (Verdict, Confidence, Explanation, EvidenceList, CorrectStatement).
        """
        # 1. Percentage equality: '25% of 200 is 50' or '25% of 200 = 50'
        pct_match = re.search(r'(\d+(?:\.\d+)?)\s*%\s*of\s*(\d+(?:\.\d+)?)\s*(?:is|=|==)\s*(\d+(?:\.\d+)?)', claim, re.IGNORECASE)
        if pct_match:
            pct = float(pct_match.group(1))
            total = float(pct_match.group(2))
            claimed_res = float(pct_match.group(3))

            actual_res = (pct / 100.0) * total
            is_correct = abs(actual_res - claimed_res) < 1e-9

            verdict = FactVerdict.TRUE if is_correct else FactVerdict.FALSE
            val_str = int(actual_res) if actual_res.is_integer() else actual_res

            if is_correct:
                exp = f"{pct}% of {total} is indeed {claimed_res}."
                correct_stmt = None
            else:
                exp = f"{pct}% of {total} evaluates to {val_str}, not {claimed_res}."
                correct_stmt = f"{pct}% of {total} is {val_str}."

            ev = [f"Independent mathematical calculation: ({pct} / 100) * {total} = {val_str}."]
            return verdict, 100, exp, ev, correct_stmt

        # 2. Natural language comparison: 'X is greater/less than Y'
        comp_match = re.search(
            r'(.+?)\s+is\s+(greater\s+than|more\s+than|less\s+than|equal\s+to)\s+(.+)',
            claim,
            flags=re.IGNORECASE
        )
        if comp_match:
            lhs_raw, op, rhs_raw = comp_match.group(1).strip(), comp_match.group(2).lower(), comp_match.group(3).strip()
            lhs_val, err1 = self.evaluate_safe(lhs_raw)
            rhs_val, err2 = self.evaluate_safe(rhs_raw)

            if lhs_val is not None and rhs_val is not None:
                if "greater" in op or "more" in op:
                    is_true = float(lhs_val) > float(rhs_val)
                    rel_sym = ">"
                elif "less" in op:
                    is_true = float(lhs_val) < float(rhs_val)
                    rel_sym = "<"
                else:
                    is_true = float(lhs_val) == float(rhs_val)
                    rel_sym = "=="

                verdict = FactVerdict.TRUE if is_true else FactVerdict.FALSE
                ev = [f"Evaluated LHS ({lhs_raw}) = {lhs_val}, RHS ({rhs_raw}) = {rhs_val}. Inequality tested: {lhs_val} {rel_sym} {rhs_val}."]
                
                if is_true:
                    exp = f"The statement is mathematically correct: {lhs_val} is {op} {rhs_val}."
                    correct_stmt = None
                else:
                    exp = f"The statement is mathematically false: {lhs_val} is not {op} {rhs_val}."
                    opp = "greater than" if "less" in op else "less than"
                    correct_stmt = f"{lhs_raw} is {opp} {rhs_raw}."
                return verdict, 100, exp, ev, correct_stmt

        # 3. Symbolic inequality: 'X > Y', 'X < Y'
        ineq_match = re.search(r'(.+?)\s*(>=|<=|>|<)\s*(.+)', claim)
        if ineq_match:
            lhs_raw, op, rhs_raw = ineq_match.group(1), ineq_match.group(2), ineq_match.group(3)
            lhs_val, err1 = self.evaluate_safe(lhs_raw)
            rhs_val, err2 = self.evaluate_safe(rhs_raw)
            if lhs_val is not None and rhs_val is not None:
                op_map = {
                    '>': float(lhs_val) > float(rhs_val),
                    '<': float(lhs_val) < float(rhs_val),
                    '>=': float(lhs_val) >= float(rhs_val),
                    '<=': float(lhs_val) <= float(rhs_val),
                }
                is_true = op_map[op]
                verdict = FactVerdict.TRUE if is_true else FactVerdict.FALSE
                ev = [f"Calculated LHS = {lhs_val}, RHS = {rhs_val}. Condition: {lhs_val} {op} {rhs_val} -> {is_true}."]
                exp = f"Evaluating both sides: LHS = {lhs_val} and RHS = {rhs_val}. The condition '{lhs_val} {op} {rhs_val}' is {verdict.value}."
                correct_stmt = None if is_true else f"{lhs_raw.strip()} is not {op} {rhs_raw.strip()}."
                return verdict, 100, exp, ev, correct_stmt

        # 4. Standard equation: '2 + 2 = 5' or '10 × 5 = 50'
        eq_match = re.search(r'(.+?)\s*(?:==|=)\s*(.+)', claim)
        if eq_match:
            lhs_raw = eq_match.group(1).strip()
            rhs_raw = eq_match.group(2).strip()

            lhs_val, err_lhs = self.evaluate_safe(lhs_raw)
            rhs_val, err_rhs = self.evaluate_safe(rhs_raw)

            if lhs_val is not None and rhs_val is not None:
                diff = sympy.simplify(lhs_val - rhs_val)
                is_equal = (diff == 0)

                verdict = FactVerdict.TRUE if is_equal else FactVerdict.FALSE
                ev = [f"Calculated LHS ({lhs_raw}) = {lhs_val}, RHS ({rhs_raw}) = {rhs_val}."]

                if is_equal:
                    exp = f"The mathematical equation holds true: {lhs_raw} correctly equals {rhs_val}."
                    correct_stmt = None
                else:
                    exp = f"The mathematical equation is false. {lhs_raw} evaluates to {lhs_val}, not {rhs_val}."
                    correct_stmt = f"{lhs_raw} = {lhs_val}"

                return verdict, 100, exp, ev, correct_stmt

        # 5. Pure calculation without equality: '(25 + 15) * 2'
        val, err = self.evaluate_safe(claim)
        if val is not None:
            val_str = str(int(val)) if (isinstance(val, sympy.Float) and val == int(val)) else str(val)
            ev = [f"Evaluated expression via exact symbolic arithmetic: {val_str}."]
            exp = f"The expression '{claim}' evaluates to {val_str}."
            return FactVerdict.TRUE, 100, exp, ev, f"{claim} = {val_str}"

        # Fallback
        return FactVerdict.UNVERIFIED, 30, f"Unable to parse mathematical expression: {claim}", [], None
