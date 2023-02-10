class JAPipelineRun:
    """
    Runs slices of modeling pipeline
    """

    def __init__(self):
        """
        The constructor method that initializes the object's attributes.
        """

    def end2end_run(self):
        """
        Runs end to end pipeline.
        """
        path = os.getcwd()
        bootstrap_project(Path(path))
        session_start = KedroSession.create()
    
        with session_start:
            session_start.run(pipeline_name="run_model_end_to_end")
            