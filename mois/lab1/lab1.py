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

class AdmissionEngine(KnowledgeEngine):
    def __init__(self):
        super().__init__()
        self.universities_db = [
            {"name": "BSUIR_AI", "subjects": ["math", "physics", "english"], "passing_score": 250},
            {"name": "BSU_Math", "subjects": ["math", "physics", "russian"], "passing_score": 280},
            {"name": "Simple_College", "subjects": ["math", "russian", "history"], "passing_score": 150},
        ]

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

    @Rule(
        UniRequirements(
            name=MATCH.uni_name,
            subjects=MATCH.subjs,
            passing_score=MATCH.pass_score
        ),
        NOT(AdmissionResult(university=MATCH.uni_name))
    )
    def check_admission(self, uni_name, subjs, pass_score):
        total_score = 0
        missing_subjects = []

        for subject in subjs:
            found = False
            for fact in self.facts.values():
                if isinstance(fact, Score) and fact['subject'] == subject:
                    total_score += fact['score']
                    found = True
                    break
            
            if not found:
                missing_subjects.append(subject)

        if missing_subjects:
            print(f"Недостаточно данных для вуза '{uni_name}'. Не хватает предметов: {missing_subjects}")
            return

        if total_score >= pass_score:
            status = "ПОСТУПИЛ"
            msg = f"Поздравляем! Вы проходите в {uni_name}. Баллы: {total_score}/{pass_score}"
        else:
            status = "НЕ ПОСТУПИЛ"
            msg = f"Вы не проходите в {uni_name}. Ваши баллы: {total_score}, нужно: {pass_score}"

        print(msg)
        
        self.declare(AdmissionResult(
            university=uni_name,
            status=status,
            total_score=total_score,
            required_score=pass_score
        ))

if __name__ == "__main__":
    print("=== Система проверки поступления ===")
    print("Доступные предметы для примера: math, physics, english, russian, history")
    print("(Вы можете вводить любые названия, главное — чтобы они совпадали с требованиями вуза)\n")

    user_scores = {}
    
    while True:
        subject = input("Введите название предмета (или 'стоп' для завершения ввода): ").strip().lower()
        
        if subject == 'стоп' or subject == 'stop':
            break
        
        if not subject:
            continue

        try:
            score_input = input(f"Введите балл за предмет '{subject}': ").strip()
            score = int(score_input)
            
            if score < 0:
                print("Балл не может быть отрицательным. Попробуйте снова.")
                continue
                
            user_scores[subject] = score
            print(f"Принято: {subject} = {score}\n")
            
        except ValueError:
            print("Ошибка: введите целое число для балла.\n")

    if user_scores:
        engine = AdmissionEngine()
        engine.reset()
        
        engine.init_universities()
        
        engine.init_applicant(user_scores)
        
        print("\n--- Результаты анализа ---")
        engine.run()
    else:
        print("Баллы не введены. Завершение работы.")