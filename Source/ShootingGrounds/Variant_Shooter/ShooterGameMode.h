// Copyright Epic Games, Inc. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "GameFramework/GameModeBase.h"
#include "ShooterGameMode.generated.h"

class UShooterUI;

/**
 *  Simple GameMode for a first person shooter game
 *  Manages game UI
 *  Keeps track of team scores
 */
UCLASS(abstract)
class SHOOTINGGROUNDS_API AShooterGameMode : public AGameModeBase
{
	GENERATED_BODY()
	
protected:

	/** Type of UI widget to spawn */
	UPROPERTY(EditAnywhere, Category="Shooter")
	TSubclassOf<UShooterUI> ShooterUIClass;

	/** Pointer to the UI widget */
	TObjectPtr<UShooterUI> ShooterUI;

	/** Map of scores by team ID */
	TMap<uint8, int32> TeamScores;

protected:

	/** Gameplay initialization */
	virtual void BeginPlay() override;

	virtual void Tick(float DeltaSeconds) override;

	UFUNCTION(BlueprintCallable, Category="Shooter")
	void StartRound();

	UFUNCTION()
	void HandleLevelEnd();

	UFUNCTION()
	void CalculateAccuracy();
	
	UFUNCTION()
	void CalculateAverageSpawnTime();

	UFUNCTION()
	void EnablePlayerInput();

	UFUNCTION()
	void DisablePlayerInput();

	APlayerController* PlayerController = nullptr;

	FTimerHandle LevelEndTimerHandle;

	int32 CurrentRound = 1;
	int32 MaxRounds = 3;

	float TimeRemaining = 0.0f;

	bool bWaitingForRoundStart = true;

public:

	AShooterGameMode();

	// Accuracy tracking
	int32 SuccessfulHits = 0;
	int32 MissedShots = 0;
	float Accuracy = 0.f;

	// Average reaction time tracking
	TArray<float> TargetSpawnTimes;
	TArray<float> TargetShotTimes;

	/** Increases the score for the given team */
	void IncrementTeamScore(uint8 TeamByte);
};
