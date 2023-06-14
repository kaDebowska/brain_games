import random
from inc.user import User


class ColorCraze:
    def __init__(self):
        self.colors_dict = {
            'czerwony': '#ea0505',
            'zielony': 'green',
            'niebieski': 'blue',
            'brązowy': '#77340a',
            'różowy': 'deeppink',
            'czarny': 'black',
            'fioletowy': 'purple'
        }
        self.values = ['czerwony', 'zielony', 'niebieski', 'brązowy', 'różowy', 'czarny', 'fioletowy']
        self.colors = ['#ea0505', 'green', 'blue', '#77340a', 'deeppink', 'black', 'purple']
        self.task_type = ''
        self.task = []
        self.correct_answer = []
        self.answers = {}
        self.player = User()

    def choose_task_type(self):
        task_type = random.randint(1, 2)
        if task_type == 1:
            self.task_type = 'znaczenie'
        else:
            self.task_type = 'kolor'
        print('task_type', self.task_type)
        return self.task_type

    def choose_task(self):
        index = random.randint(0, len(self.values) - 1)
        self.task.append(self.values[index])
        colors = [color for color in self.colors if color != self.colors_dict[self.task[0]]]
        self.task.append(colors[random.randint(0, len(colors) - 1)])
        print('task', self.task)
        return self.task

    def choose_correct_answer(self):
        if self.task_type == 'znaczenie':
            self.correct_answer.append(self.task[0])
            excludes_colors = [self.task[1], self.colors_dict[self.task[0]]]
            colors = [color for color in self.colors if color not in excludes_colors]
            # print('colors', colors)
            index = random.randint(0, len(colors) - 1)
            self.correct_answer.append(colors[index])
        else:
            value_of_task_color = list(self.colors_dict.keys())[list(self.colors_dict.values()).index(self.task[1])]
            print('value_of_task_color', value_of_task_color)
            values = [value for value in self.values if value not in [self.task[0], value_of_task_color]]
            # print('values', values)
            index = random.randint(0, len(values) - 1)
            self.correct_answer.append(values[index])
            self.correct_answer.append(self.task[1])
        print('correct_answer', self.correct_answer)
        return self.correct_answer

    def generate_answers(self):
        if self.task_type == 'znaczenie':
            print('task', self.task)
            values = [value for value in self.values if value != self.correct_answer[0]]
            random.shuffle(values)
            answers_colors = [self.task[1], self.colors_dict[self.correct_answer[0]], self.correct_answer[1]]
            print('answers_colors', answers_colors)
            colors = [color for color in self.colors if color not in answers_colors]
            print('colors', colors)
            index = random.randint(0, len(colors) - 1)
            answers_colors.append(colors[index])
            answers_colors.remove(self.correct_answer[1])
            random.shuffle(answers_colors)
            for i in range(3):
                self.answers[values[i]] = answers_colors[i]
        else:
            colors = [color for color in self.colors if color != self.correct_answer[1]]
            random.shuffle(colors)
            answers_values = [self.task[0]]
            value_of_task_color = list(self.colors_dict.keys())[list(self.colors_dict.values()).index(self.task[1])]
            answers_values.append(value_of_task_color)
            values = [value for value in self.values if value not in answers_values]
            print('values', values)
            for value in values:
                if value == self.correct_answer[0]:
                    values.remove(value)
            index = random.randint(0, len(values)-1)
            answers_values.append(values[index])
            print('answers_values', answers_values)
            random.shuffle(answers_values)
            for i in range(3):
                self.answers[answers_values[i]] = colors[i]
        print('answers', self.answers)
        self.answers[self.correct_answer[0]] = self.correct_answer[1]
        set_answers = list(set(self.answers))
        self.answers = {i: self.answers[i] for i in set_answers}
        print('answers', self.answers)
        return self.answers
