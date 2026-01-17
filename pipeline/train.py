from models.linear_baseline import LinearBaselineModel

def train_baseline_model(df):
    """
    Instantiates and trains the Linear Baseline Model.
    """
    model = LinearBaselineModel()
    model.train(df)
    return model
