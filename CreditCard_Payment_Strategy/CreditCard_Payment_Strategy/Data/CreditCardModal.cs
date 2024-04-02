namespace CreditCard_Payment_Strategy.Data
{
    public class CreditCardModal
    {
        public int id { get; set; }
        public int user_id { get; set; }
        public string username { get; set; }
        public string card_name { get; set; }
        public double card_limit { get; set; }
        public double ten_percent_limit { get { return card_limit * 0.1; } }
        public double thirty_percent_limit { get { return card_limit * 0.3; } }
        public double current_balance { get; set; }
        public double percent_utilized => card_limit != 0 ? Math.Round((current_balance / card_limit) * 100, 2) : 0;

    }

    public class CreditCardResponse
    {
        public CreditCardModal[] credit_cards { get; set; }
    }   
}

