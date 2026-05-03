from experta import *

class Score(Fact):
    subject = Field(str)
    score = Field(int)

class UniRequirements(Fact):
    name = Field(str)
    subjects = Field(list)
    passing_score = Field(int)

class AdmissionResult(Fact):
    university = Field(str)
    status = Field(str)
    total_score = Field(int)
    required_score = Field(int)

# Промежуточный факт для цепочки правил
class UniValidated(Fact):
    name = Field(str)
    total_score = Field(int)

class AdmissionEngine(KnowledgeEngine):
    def __init__(self):
        super().__init__()
        self.universities_db = [
            {"name": "BSUIR_AI", "subjects": ["math", "physics", "english"], "passing_score": 250},
            {"name": "BSU_Math", "subjects": ["math", "physics", "russian"], "passing_score": 280},
            {"name": "Simple_College", "subjects": ["math", "russian", "history"], "passing_score": 150},
        ]

    def _get_subject_score(self, subject):
        """Вспомогательный метод для поиска балла по предмету"""
        for fact in self.facts.values():
            if isinstance(fact, Score) and fact['subject'] == subject:
                return fact['score']
        return None

    def init_applicant(self, scores_dict: dict):
        for subj, score in scores_dict.items():
            self.declare(Score(subject=subj, score=score))

    def init_universities(self):
        for uni in self.universities_db:
            self.declare(UniRequirements(
                name=uni['name'],
                subjects=uni['subjects'],
                passing_score=uni['passing_score']
            ))

    # 🔹 ПРАВИЛО 1: Проверка наличия предметов и минимального порога по каждому (например, 40)
    @Rule(
        UniRequirements(name=MATCH.uni_name, subjects=MATCH.subjs, passing_score=MATCH.pass_score),
        NOT(UniValidated(name=MATCH.uni_name)),
        NOT(AdmissionResult(university=MATCH.uni_name))
    )
    def validate_subjects(self, uni_name, subjs, pass_score):
        total = 0
        for subject in subjs:
            score = self._get_subject_score(subject)
            if score is None:
                print(f"⚠️ {uni_name}: Отказ. Не указан балл за предмет '{subject}'.")
                self.declare(AdmissionResult(university=uni_name, status="НЕТ ДАННЫХ", total_score=0, required_score=pass_score))
                return
            if score < 40:  # Типичный минимальный порог по предмету
                print(f"⛔ {uni_name}: Отказ. Балл за '{subject}' ({score}) ниже минимального (40).")
                self.declare(AdmissionResult(university=uni_name, status="НИЖЕ МИНИМУМА ПО ПРЕДМЕТУ", total_score=total, required_score=pass_score))
                return
            total += score
        
        # Если все проверки пройдены, создаём промежуточный факт для следующих правил
        self.declare(UniValidated(name=uni_name, total_score=total))

    # 🔹 ПРАВИЛО 2: Проходной балл набран -> Поступление
    @Rule(
        UniValidated(name=MATCH.uni_name, total_score=MATCH.total),
        UniRequirements(name=MATCH.uni_name, passing_score=MATCH.pass_score),
        NOT(AdmissionResult(university=MATCH.uni_name))
    )
    def check_pass(self, uni_name, total, pass_score):
        if total >= pass_score:
            self.declare(AdmissionResult(university=uni_name, status="ПОСТУПИЛ", total_score=total, required_score=pass_score))
            print(f"✅ {uni_name}: ПОСТУПИЛ! (Ваши баллы: {total} / Проходной: {pass_score})")

    # 🔹 ПРАВИЛО 3: Проходной балл НЕ набран -> Отказ
    @Rule(
        UniValidated(name=MATCH.uni_name, total_score=MATCH.total),
        UniRequirements(name=MATCH.uni_name, passing_score=MATCH.pass_score),
        NOT(AdmissionResult(university=MATCH.uni_name))
    )
    def check_fail(self, uni_name, total, pass_score):
        if total < pass_score:
            self.declare(AdmissionResult(university=uni_name, status="НЕ ПОСТУПИЛ", total_score=total, required_score=pass_score))
            print(f"❌ {uni_name}: НЕ ПОСТУПИЛ. (Ваши баллы: {total} / Нужно: {pass_score})")


if __name__ == "__main__":
    print("=== Система проверки поступления ===")
    print("Доступные предметы: math, physics, english, russian, history")
    print("(Вводите названия на латинице, как в списке)\n")

    user_scores = {}
    
    while True:
        subject = input("Введите предмет (или 'стоп' для завершения): ").strip().lower()
        
        if subject in ('стоп', 'stop', ''):
            break
        
        try:
            score_input = input(f"Балл за '{subject}': ").strip()
            score = int(score_input)
            
            if not (0 <= score <= 100):
                print("⚠️ Балл должен быть от 0 до 100. Попробуйте снова.")
                continue
                
            user_scores[subject] = score
            print(f"✔️ Принято: {subject} = {score}\n")
            
        except ValueError:
            print("❌ Ошибка: введите целое число.\n")

    if user_scores:
        engine = AdmissionEngine()
        engine.reset()
        
        engine.init_universities()
        engine.init_applicant(user_scores)
        
        print("\n--- 📊 Результаты анализа ---")
        engine.run()
    else:
        print("Баллы не введены. Завершение работы.")