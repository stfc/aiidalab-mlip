"""Test application state models."""

from aiidalab_mlip.models import CodeModel, TaskModel
from aiidalab_mlip.models.base import Model


def test_base_model():
    """Test base Model traitlets."""
    model = Model()
    assert hasattr(model, "submitted")
    assert model.submitted is False
    model.submitted = True
    assert model.submitted is True


def test_task_model():
    """Test TaskModel attributes and traitlets."""
    task_model = TaskModel()
    assert hasattr(task_model, "task")
    assert hasattr(task_model, "task_parameters")
    assert task_model.task == ""
    assert task_model.task_parameters == {}

    task_model.task = "geomopt"
    task_model.task_parameters = {"fmax": 0.05}
    assert task_model.task == "geomopt"
    assert task_model.task_parameters["fmax"] == 0.05


def test_code_model():
    """Test CodeModel attributes and traitlets."""
    code_model = CodeModel()
    assert hasattr(code_model, "ncpus")
    assert code_model.ncpus == 4
    code_model.ncpus = 8
    assert code_model.ncpus == 8

    code_model.arch = "mace_mp"
    code_model.device = "cpu"
    assert code_model.arch == "mace_mp"
    assert code_model.device == "cpu"


def test_structure_model():
    """Test StructureModel attributes."""
    from ase import Atoms
    from aiidalab_mlip.models import StructureModel

    sm = StructureModel()
    assert sm.structure is None
    assert sm.filename == ""

    atoms = Atoms("H2", positions=[[0, 0, 0], [0, 0, 0.74]])
    sm.structure = atoms
    sm.filename = "h2.xyz"
    assert len(sm.structure) == 2
    assert sm.filename == "h2.xyz"


def test_prediction_and_results_model():
    """Test PredictionModel and ResultsModel attributes."""
    from aiidalab_mlip.models import PredictionModel, ResultsModel

    pm = PredictionModel()
    assert pm.calculation_type == "geometry_opt"
    pm.calculation_type = "singlepoint"
    assert pm.calculation_type == "singlepoint"

    rm = ResultsModel()
    assert rm.calculation_pk == 0
    rm.calculation_pk = 42
    assert rm.calculation_pk == 42


def test_main_app_model():
    """Test MainAppModel sub-model composition."""
    from aiidalab_mlip.models import MainAppModel

    app_model = MainAppModel()
    assert app_model.process_label == ""
    assert app_model.process_description == ""
    assert hasattr(app_model, "structure_model")
    assert hasattr(app_model, "mlip_model")
    assert hasattr(app_model, "task_model")
    assert hasattr(app_model, "prediction_model")
    assert hasattr(app_model, "results_model")
