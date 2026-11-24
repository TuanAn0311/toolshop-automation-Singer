Feature: Cart pricing after a product search
  As a shopper
  I want to find a product and add the quantity I need to my cart
  So that I can verify what I will pay before checking out

  Scenario Outline: The cart charges for the selected quantity
    Given I am browsing the catalog with an empty cart
    When I search for "<keyword>" and select "<product>"
    And I add <quantity> units to my cart
    Then my cart shows <quantity> units of "<product>"
    And the line price is the product's unit price times the quantity
    And the cart total is the sum of its line prices

    Examples:
      | keyword | product            | quantity |
      | pliers  | Combination Pliers | 1        |
      | hammer  | Claw Hammer        | 3        |
