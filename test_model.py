from model import Card, HandScoring, Deck

'''
Run with pytest
'''

hands = HandScoring.HandRanks

def test_deck():
  d = Deck()
  assert len(d.cards) == 52

def check_hand(all_cards, hand_rank, hand_cards=None):
  hand = set(all_cards)
  hand_rank_obs, cards_obs = HandScoring.score(hand)
  assert cards_obs != None
  assert None not in cards_obs
  assert hand_rank_obs == hand_rank
  if hand_cards:
    assert check_eq_by_rank(cards_obs, set(hand_cards))

def check_eq_by_rank(hand1, hand2):
  hand1 = hand1.copy()
  hand2 = hand2.copy()

  for card1 in hand1:
    found = False
    for card2 in hand2:
      if card1.rank == card2.rank:
        found = True
        hand2.remove(card2)
        break
    if not found:
      return False
  return len(hand2) == 0

def test_straight_flush():
  check_hand([Card(1,1), Card(2,1), Card(3,1), Card(4,1), Card(5,1)], hands.STRAIGHT_FLUSH)
  check_hand([Card(1,2), Card(2,1), Card(3,1), Card(4,1), Card(5,1), Card(10,1)], hands.FLUSH)

def test_4_kind():
  check_hand([Card(1,1), Card(1,2), Card(1,3), Card(1,4)], hands.FOUR_KIND)

def test_fullhouse():
  check_hand([Card(1,1), Card(1,2), Card(2,1), Card(2,2), Card(2,3)], hands.FULL_HOUSE)

  # test that higher ranks are chosen for 3 pair
  check_hand(
    [Card(1,1), Card(1,2), Card(1,3), Card(2,1), Card(2,2), Card(2,3)],
    hands.FULL_HOUSE,
    hand_cards=[Card(1,1), Card(1,2), Card(2,1), Card(2,2), Card(2,3)]
  )

def test_flush():
  check_hand([Card(10,1), Card(2,1), Card(3,1), Card(4,1), Card(5,1)], hands.FLUSH)

def test_straight():
  check_hand([Card(1,1), Card(2,2), Card(3,1), Card(4,2), Card(5,3)], hands.STRAIGHT)
  
def test_3_kind():
  check_hand([Card(1,1), Card(1,2), Card(1,3)], hands.THREE_KIND)
  
def test_2_pair():
  check_hand([Card(1,1), Card(1,2), Card(2,3), Card(2,4)], hands.TWO_PAIR)

def test_pair():
  check_hand([Card(1,1), Card(1,2)], hands.ONE_PAIR)

def test_high_card():
  check_hand([Card(1,1)], hands.HIGH_CARD)

def test_compare():
  # check_hand(
  #   [Card(9,3), Card(10, 2), Card(12, 4)], hands.HIGH_CARD
  # )
  check_hand(
    [
      Card(2,2),
      Card(2,3),
      Card(4,1),
      Card(4,4),
      Card(6,1),
      Card(6,3),
      Card(7,1),
      Card(7,2),
      Card(9,1),
      Card(10,1),
      Card(11,2),
      Card(12,1),
      Card(12,3),
      Card(13,2)
    ], hands.FLUSH)