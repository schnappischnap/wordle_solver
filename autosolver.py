"""Automates opening Wordle and solving today's game."""


from pyshadow.main import Shadow
from selenium import webdriver
from selenium.common.exceptions import *
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from wordle_solver import Solver

with open("solver.config", "r") as f:
    USER_DATA_DIRECTORY = f.read().strip()
FEEDBACK_CONVERSION = {
    "absent": Solver.BLACK,
    "present": Solver.YELLOW,
    "correct": Solver.GREEN,
}


def solve(first_guess="roate"):
    """Launch Wordle and solve today's game."""
    try:
        # Get the instruction or statistics modal.
        modal = WebDriverWait(driver, 3).until(modal_exists)
        if modal.tag_name == "game-help":
            # Close instruction modal.
            shadow.find_element('game-icon[icon="close"]').click()
        else:
            # The game has already been solved.
            return
    except TimeoutException:
        pass

    guess = None
    game_rows = shadow.find_elements("game-row")
    rows = shadow.find_elements("div.row")
    for i in range(5):
        WebDriverWait(driver, 5).until(can_input)

        # Has this row already been guessed?
        if row_guess := game_rows[i].get_attribute("letters"):
            if apply_guess(rows[i], row_guess):
                return True
            guess = row_guess
            continue

        # Make the guess.
        guess = solver.best_guess() if guess else first_guess
        actions.send_keys(guess + "\n")
        actions.perform()

        if apply_guess(rows[i], guess):
            break
        guess = solver.best_guess()

    # Copy the results to clipboard.
    WebDriverWait(driver, 5).until(modal_exists)
    shadow.find_element("button#share-button").click()


def apply_guess(row, guess):
    """Read the feedback, apply it to the solver and return True if solved."""
    feedback = tuple(
        FEEDBACK_CONVERSION[e.get_attribute("evaluation")]
        for e in shadow.find_elements(row, "game-tile")
    )

    # Return True if the game has already been solved.
    if feedback == (Solver.GREEN,) * 5:
        return True

    # Filter the possible guesses.
    solver.apply_feedback(guess, feedback)


def modal_exists(_driver):
    """Return either the <game-stats> or <game-help> element, if present."""
    try:
        modal = shadow.find_element("game-modal")
        modal_children = shadow.get_child_elements(modal)
        if not modal_children:
            return False
    except NoSuchElementException:
        return False
    except ElementNotVisibleException:
        return False
    return modal_children[0]


def can_input(_driver):
    """Return True when animations have finished and a guess can be inputted."""
    try:
        return all(
            e.get_attribute("data-animation") == "idle"
            for e in shadow.find_elements("div.tile")
        )
    except NoSuchElementException:
        return False
    except StaleElementReferenceException:
        return all(
            e.get_attribute("data-animation") == "idle"
            for e in shadow.find_elements("div.tile")
        )


if __name__ == "__main__":
    solver = Solver()

    options = webdriver.ChromeOptions()
    # Use a specific user data directory (to save your guesses).
    # options.add_argument(f"user-data-dir={USER_DATA_DIRECTORY}")

    driver = webdriver.Chrome(options=options)
    driver.get("https://www.powerlanguage.co.uk/wordle/")

    shadow = Shadow(driver)
    actions = ActionChains(driver)

    try:
        solve()
    finally:
        driver.quit()
