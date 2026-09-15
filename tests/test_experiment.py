import pytest

from launchlab.experiment import ExperimentConfig


def test_default_config_is_valid():
    config = ExperimentConfig(n_users=1_000)
    assert config.n_users == 1_000
    assert config.treatment_share == pytest.approx(0.5)
    assert config.exposure_probability == pytest.approx(1.0)


@pytest.mark.parametrize(
    ("kwargs", "message"),
    [
        ({"n_users": 0}, "n_users"),
        ({"n_users": 100, "treatment_share": 0.0}, "treatment_share"),
        ({"n_users": 100, "treatment_share": 1.0}, "treatment_share"),
        ({"n_users": 100, "exposure_probability": -0.1}, "exposure_probability"),
        ({"n_users": 100, "baseline_conversion": 0.0}, "baseline_conversion"),
        (
            {
                "n_users": 100,
                "baseline_conversion": 0.95,
                "treatment_effect": 0.10,
            },
            r"baseline_conversion \+ treatment_effect",
        ),
    ],
)
def test_invalid_config_raises(kwargs, message):
    with pytest.raises(ValueError, match=message):
        ExperimentConfig(**kwargs)
