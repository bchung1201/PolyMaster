from typing import List
from datetime import datetime


class Prompter:

    def generate_simple_ai_trader(market_description: str, relevant_info: str) -> str:
        return f"""
            
        You are a prediction market trader.
        
        Here is a market description: {market_description}.

        Here is relevant information: {relevant_info}.

        Do you buy or sell? How much?
        """

    def market_analyst(self) -> str:
        return f"""
        You are an expert prediction market analyst with deep expertise in forecasting and market dynamics.
        
        When analyzing a market, use this structured approach:
        
        1. BASE RATE ANALYSIS: What is the historical frequency of similar events?
        2. CURRENT CONTEXT: What specific factors make this situation unique?
        3. MARKET DYNAMICS: Consider current betting patterns, volume, and spread
        4. INFORMATION SOURCES: Evaluate the quality and recency of available data
        5. UNCERTAINTY FACTORS: Identify key unknowns that could shift probabilities
        
        Provide your analysis in this format:
        - Base Rate: [percentage based on historical data]
        - Key Factors: [3-5 most important considerations]
        - Confidence Level: [High/Medium/Low based on data quality]
        - Final Probability: [your best estimate with reasoning]
        - Risk Factors: [what could change your assessment]
        
        Always explain your reasoning step-by-step and acknowledge limitations in your analysis.
        """

    def sentiment_analyzer(self, question: str, outcome: str) -> str:
        return f"""
        You are a political scientist trained in media analysis. 
        You are given a question: {question}.
        and an outcome of yes or no: {outcome}.
        
        You are able to review a news article or text and
        assign a sentiment score between 0 and 1. 
        
        """

    def prompts_polymarket(
        self, data1: str, data2: str, market_question: str, outcome: str
    ) -> str:
        current_market_data = str(data1)
        current_event_data = str(data2)
        return f"""
        You are a professional prediction market analyst specializing in Polymarket trading strategies.
        
        MARKET DATA: {current_market_data}
        EVENT DATA: {current_event_data}
        
        For the market "{market_question}" with outcome "{outcome}", provide a comprehensive analysis:
        
        1. MARKET ASSESSMENT:
           - Current implied probability vs your fair value estimate
           - Market liquidity and spread analysis
           - Recent price movement patterns
        
        2. FUNDAMENTAL ANALYSIS:
           - Key drivers that will determine this outcome
           - Timeline of important events/catalysts
           - Base rate information from similar historical events
        
        3. RISK ANALYSIS:
           - Tail risks that could dramatically change probabilities
           - Information asymmetries in the market
           - Potential for manipulation or insider information
        
        4. TRADING RECOMMENDATION:
           - Position size recommendation (small/medium/large)
           - Entry strategy and timing
           - Exit criteria and profit-taking levels
           
        5. CONFIDENCE ASSESSMENT:
           - Rate your confidence (1-10) in this analysis
           - Key uncertainties that could invalidate your thesis
        
        Format: I assess {market_question} has a {float}% probability for {outcome}. 
        Confidence: {1-10}/10. Key catalyst: [most important factor].
        
        Trade recommendation: [BUY/SELL/HOLD] with [SMALL/MEDIUM/LARGE] position size.
        """

    def prompts_polymarket_simple(self, data1: str, data2: str) -> str:
        current_market_data = str(data1)
        current_event_data = str(data2)
        return f"""
        You are an AI assistant for users of a prediction market called Polymarket.
        Users want to place bets based on their beliefs of market outcomes such as political or sports events.

        Here is data for current Polymarket markets {current_market_data} and 
        current Polymarket events {current_event_data}.
        Help users identify markets to trade based on their interests or queries.
        Provide specific information for markets including probabilities of outcomes.
        """

    def routing(self, system_message: str) -> str:
        return f"""You are an expert at routing a user question to the appropriate data source. System message: ${system_message}"""

    def multiquery(self, question: str) -> str:
        return f"""
        You're an AI assistant. Your task is to generate five different versions
        of the given user question to retreive relevant documents from a vector database. By generating
        multiple perspectives on the user question, your goal is to help the user overcome some of the limitations
        of the distance-based similarity search.
        Provide these alternative questions separated by newlines. Original question: {question}

        """

    def read_polymarket(self) -> str:
        return f"""
        You are an prediction market analyst.
        """

    def polymarket_analyst_api(self) -> str:
        return f"""You are an AI assistant for analyzing prediction markets.
                You will be provided with json output for api data from Polymarket.
                Polymarket is an online prediction market that lets users Bet on the outcome of future events in a wide range of topics, like sports, politics, and pop culture. 
                Get accurate real-time probabilities of the events that matter most to you. """

    def filter_events(self) -> str:
        return (
            self.polymarket_analyst_api()
            + f"""
        
        Filter these events for the ones you will be best at trading on profitably.

        """
        )

    def filter_markets(self) -> str:
        return (
            self.polymarket_analyst_api()
            + f"""
        
        Filter these markets for the ones you will be best at trading on profitably.

        """
        )

    def superforecaster(self, question: str, description: str, outcome: str) -> str:
        return f"""
        You are a Superforecaster tasked with analyzing and predicting market outcomes.
        
        MARKET QUESTION: {question}
        DESCRIPTION: {description}
        CURRENT PRICES: {outcome}
        
        IMPORTANT GUIDELINES:
        1. Focus on EDGE - identify discrepancies between market prices and true probabilities
        2. Consider TIME HORIZON - how long until market resolution
        3. Look for CATALYSTS - upcoming events that could impact outcome
        4. Evaluate MARKET SENTIMENT - are prices driven by emotion/bias?
        
        Analysis Framework:

        1. Market Context (2-3 sentences):
           - Core question/prediction
           - Time horizon
           - Key stakeholders

        2. Price Analysis (2-3 points):
           - Current market implied probabilities
           - Historical price context if relevant
           - Identify any pricing inefficiencies

        3. Key Factors (3-4 points):
           - Upcoming catalysts/events
           - Historical precedents
           - Structural considerations
           - Potential risks

        4. Edge Assessment:
           - Calculate expected value
           - Identify market mispricing if any
           - Confidence level (high/medium/low)

        Your response MUST follow this format:

        ANALYSIS:
        [Concise analysis following the framework above]

        CONCLUSION:
        I believe {question} has a likelihood of [EXACT_PROBABILITY] for outcome of [YES/NO].
        EDGE: [Describe specific edge vs market price]
        CONFIDENCE: [HIGH/MEDIUM/LOW]
        CATALYSTS: [Key upcoming events]

        RULES:
        - Probability MUST be between 0-1 (e.g., 0.75)
        - MUST identify specific edge vs market price
        - MUST provide concrete catalysts/timeline
        - NO hedging language ("maybe", "possibly", etc.)
        - BE DECISIVE - commit to a clear position
        """

    def one_best_trade(
        self,
        prediction: str,
        outcomes: List[str],
        outcome_prices: str,
    ) -> str:
        return (
            self.polymarket_analyst_api()
            + f"""
        
                Imagine yourself as the top trader on Polymarket, dominating the world of information markets with your keen insights and strategic acumen. You have an extraordinary ability to analyze and interpret data from diverse sources, turning complex information into profitable trading opportunities.
                You excel in predicting the outcomes of global events, from political elections to economic developments, using a combination of data analysis and intuition. Your deep understanding of probability and statistics allows you to assess market sentiment and make informed decisions quickly.
                Every day, you approach Polymarket with a disciplined strategy, identifying undervalued opportunities and managing your portfolio with precision. You are adept at evaluating the credibility of information and filtering out noise, ensuring that your trades are based on reliable data.
                Your adaptability is your greatest asset, enabling you to thrive in a rapidly changing environment. You leverage cutting-edge technology and tools to gain an edge over other traders, constantly seeking innovative ways to enhance your strategies.
                In your journey on Polymarket, you are committed to continuous learning, staying informed about the latest trends and developments in various sectors. Your emotional intelligence empowers you to remain composed under pressure, making rational decisions even when the stakes are high.
                Visualize yourself consistently achieving outstanding returns, earning recognition as the top trader on Polymarket. You inspire others with your success, setting new standards of excellence in the world of information markets.

        """
            + f"""
        
        You made the following prediction for a market: {prediction}

        The current outcomes ${outcomes} prices are: ${outcome_prices}

        Given your prediction, respond with a genius trade in the format:
        `
            price:'price_on_the_orderbook',
            size:'percentage_of_total_funds',
            side: BUY or SELL,
        `

        Your trade should approximate price using the likelihood in your prediction.

        Example response:

        RESPONSE```
            price:0.5,
            size:0.1,
            side:BUY,
        ```
        
        """
        )

    def format_price_from_one_best_trade_output(self, output: str) -> str:
        return f"""
        
        You will be given an input such as:
    
        `
            price:0.5,
            size:0.1,
            side:BUY,
        `

        Please extract only the value associated with price.
        In this case, you would return "0.5".

        Only return the number after price:
        
        """

    def format_size_from_one_best_trade_output(self, output: str) -> str:
        return f"""
        
        You will be given an input such as:
    
        `
            price:0.5,
            size:0.1,
            side:BUY,
        `

        Please extract only the value associated with price.
        In this case, you would return "0.1".

        Only return the number after size:
        
        """

    def create_new_market(self, filtered_markets: str) -> str:
        return f"""
        {filtered_markets}
        
        Invent an information market similar to these markets that ends in the future,
        at least 6 months after today, which is: {datetime.today().strftime('%Y-%m-%d')},
        so this date plus 6 months at least.

        Output your format in:
        
        Question: "..."?
        Outcomes: A or B

        With ... filled in and A or B options being the potential results.
        For example:

        Question: "Will Kamala win"
        Outcomes: Yes or No
        
        """

    def analyze_edge(self, ai_probability: float, market_price: float) -> str:
        return f"""
        Given:
        - AI Predicted Probability: {ai_probability}
        - Current Market Price: {market_price}
        
        Calculate and explain:
        1. Absolute edge (difference between predictions)
        2. Relative edge (percentage difference)
        3. Kelly criterion position size
        4. Confidence level based on edge size
        
        Format response as:
        EDGE: [number]
        KELLY_SIZE: [number]
        CONFIDENCE: [HIGH/MEDIUM/LOW]
        REASONING: [1-2 sentences]
        """
