"""Solves a Wordle game in 5-or-fewer moves, with an average of 3.482."""


from collections import Counter
import itertools


class Solver:
    BLACK = 0
    YELLOW = 1
    GREEN = 2

    def __init__(self):
        with open("words.txt", "r") as f:
            self.ALL_GUESSES = [line.strip() for line in f]
        with open("all_words.txt", "r") as f:
            self.ALL_WORDS = [line.strip() for line in f] + self.ALL_GUESSES
        self.words = self.ALL_GUESSES

    def solve(self, first_guess="roate", hard_mode=False):
        """Provides the next best guess given the feedback."""
        guess = first_guess
        print("Input feedback as a sequence of 5 letters b=black y=yellow g=green (e.g. bbygb)")
        while True:
            feedback = read_feedback_input(f"{guess}\t Feedback: ")
            if feedback == (Solver.GREEN,) * 5:
                return

            self.apply_feedback(guess, feedback)
            print(self.words)

            guess = self.best_guess(hard_mode)

    def apply_feedback(self, guess, feedback):
        """Filter out any words that don't fit the feedback pattern."""
        self.words = [word for word in self.words 
                      if evaluate(guess, word) == feedback and word != guess]

    def best_guess(self, hard_mode=False):
        """Return the best guess using a minimax algorithm."""
        # There isn't any point finding the "best" guess if there are fewer than 3 words left.
        if len(self.words) < 3:
            return self.words[0]

        possible_guesses = self.words if hard_mode else self.ALL_WORDS

        # Score each word by the number of instances of the most common colour-tuple combination.
        total = len(self.words)
        results = [
            (guess, sum(v*v / total for v in Counter(evaluate(guess, word)
             for word in self.words).values()))
            for guess in possible_guesses
        ]

        # Get a list of words that have the lowest score.
        best_score = min(score for _, score in results)
        best_words = [word for word, score in results if score == best_score]

        # If any of the best_words are in the remaining word list, return one of them.
        if best_words_in_words := set(best_words) & set(self.words):
            return best_words_in_words.pop()
        return best_words.pop()

    def autosolve(self, first_guess, answer, hard_mode=False):
        """Return the number of guesses it takes to solve the puzzle."""
        print(f"Solving '{answer}'")

        self.words = self.ALL_GUESSES
        guess = first_guess
        for i in itertools.count(1):
            feedback = evaluate(guess, answer)
            if feedback == (Solver.GREEN,) * 5:
                return i

            self.apply_feedback(guess, feedback)

            guess = self.best_guess(hard_mode)

    def test_first_guess(self, first_guess):
        """Solves every possible solution and returns the analysis."""
        results = Counter(self.autosolve(first_guess, word)
                          for word in self.ALL_GUESSES)
        total = len(self.ALL_GUESSES)
        print("\t".join(f"{k}: {v}" for k, v in sorted(results.items())))
        print(sum((v*k)/total for k, v in results.items()))


def evaluate(guess, solution):
    """Return a tuple describing the similarities between 2 strings."""
    feedback = []
    marked = []  # Which characters in solution have been evaluated.
    for guess_c, solution_c in zip(guess, solution):
        feedback.append(Solver.GREEN if guess_c ==
                        solution_c else Solver.BLACK)
        marked.append(True if guess_c == solution_c else False)

    for i, (guess_c, feedback_colour) in enumerate(zip(guess, feedback)):
        if feedback_colour == Solver.BLACK:
            for j in range(len(guess)):
                # A repeated letter in the guess string will only show up yellow
                # if that letter is also repeated in the solution string.
                if not marked[j] and solution[j] == guess_c:
                    marked[j] = True
                    feedback[i] = Solver.YELLOW
                    break

    return tuple(feedback)


def read_feedback_input(prompt):
    """Repeatingly read a feedback input until a valid one is given, then return it."""
    while True:
        try:
            feedback = [s.lower() for s in input(f"{prompt}")]
            if len(feedback) != 5:
                print("Feedback must be 5 characters long.")
                continue
            if any(c not in "byg" for c in feedback):
                print("Only 'B' 'Y' and 'G' are valid feedback tokens.")
                continue
            break
        except:
            print("There is an error with your input.")
            continue
    return tuple({"b": Solver.BLACK, "y": Solver.YELLOW, "g": Solver.GREEN}[c] for c in feedback)


if __name__ == "__main__":
    # Solver().test_first_guess("roate")  # Takes a long time!
    Solver().solve("roate")  # Win in 3.482 turns on average, 5 maximum.
