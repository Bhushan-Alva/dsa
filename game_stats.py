class GameStats:
    """Tracks statistics for alien invasion"""
    def __init__(self, ai_game):
        """initialize statistics"""
        self.settings = ai_game.settings
        self.reset_stats()

        # high score should never be reset
        self.high_score = 0


    def reset_stats(self):
        """initialize stats that change during game"""
        self.ships_left = self.settings.ship_limit
        self.score = 0
        self.level = 1
