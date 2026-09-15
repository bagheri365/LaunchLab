from launchlab.repeated import (
    analyze_at_user_level,
    analyze_naively_at_request_level,
    simulate_repeated_user_experiment,
)


def main() -> None:
    experiment = simulate_repeated_user_experiment(
        n_users=100_000,
        baseline_user_conversion=0.05,
        treatment_effect=0.0,
        mean_requests_per_user=10.0,
        activity_shape=1.0,
        seed=7,
    )

    user = analyze_at_user_level(experiment)
    request = analyze_naively_at_request_level(experiment)

    print(f"users: {experiment.n_users:,}")
    print(f"requests: {experiment.n_requests:,}")
    print()
    print("Correct user-level analysis")
    print(f"  effect: {user.absolute_effect:.6f}")
    print(f"  SE:     {user.standard_error:.6f}")
    print(f"  95% CI: [{user.ci_low:.6f}, {user.ci_high:.6f}]")
    print()
    print("Naive request-level analysis")
    print(f"  effect: {request.absolute_effect:.6f}")
    print(f"  SE:     {request.standard_error:.6f}")
    print(f"  95% CI: [{request.ci_low:.6f}, {request.ci_high:.6f}]")
    print()
    print(
        "SE ratio (naive / correct): "
        f"{request.standard_error / user.standard_error:.3f}"
    )


if __name__ == "__main__":
    main()
