import unittest

from game.card import Card
from game.deck import CardDeck


class DeckTest(unittest.TestCase):

    def test_creation(self):
        """
        Check that the _deck is properly created
        :return:
        """
        self.deck = CardDeck()
        self.assertEqual("en", self.deck.lang_id)
        self.assertEqual(52, len(self.deck.deck))

    def test_shuffle(self):
        """
        Check that shuffeling actually changes order of cards
        :return:
        """
        self.deck = CardDeck()
        d1 = self.deck.deck.copy()

        d2 = self.deck.deck.copy()
        # We check that our two decks we copied are the same
        # This is to proof that the assertNotEqual later on works correctly
        self.assertEqual(d1, d2)

        self.deck._shuffle()
        d3 = self.deck.deck.copy()

        # Just check that we did not lose any cards through shuffeling
        self.assertEqual(52, len(d1))
        self.assertEqual(52, len(d2))
        self.assertEqual(52, len(d3))

        # Our first and third _deck should now differ
        # There is a veeeeeery tiny rest probability that after shuffeling the _deck is exactly the same as before
        # But we are ignoring that here!
        self.assertNotEqual(d1, d3)

    def test_set_up_deck(self):
        """
        Check if the set up method creates a new sorted _deck of cards
        :return:
        """
        self.deck = CardDeck()
        self.deck._set_up_deck()

        # Check if the _deck is sorted (linear ascending numbers)
        for counter in range(52):
            self.assertEqual(counter, self.deck.deck[counter].card_id)

    def test_draw(self):
        """
        Check if drawing cards works as intended
        :return:
        """
        self.deck = CardDeck()
        self.assertEqual(52, len(self.deck.deck))

        card = self.deck.pick_one_card()

        self.assertEqual(51, len(self.deck.deck))
        self.assertEqual(Card, type(card))

    def test_draw_empty(self):
        """
        Check if drawing works as intended when the _deck is empty
        :return:
        """
        pass


if __name__ == '__main__':
    unittest.main()
