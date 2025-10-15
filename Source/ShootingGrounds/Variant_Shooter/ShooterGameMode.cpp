// Copyright Epic Games, Inc. All Rights Reserved.


#include "Variant_Shooter/ShooterGameMode.h"
#include "ShooterUI.h"
#include "Kismet/GameplayStatics.h"
#include "Engine/World.h"

void AShooterGameMode::BeginPlay()
{
	Super::BeginPlay();

	// Set timer to end level in 60 seconds
    // GetWorld()->GetTimerManager().SetTimer(
    //     LevelEndTimerHandle,
    //     this,
    //     &AShooterGameMode::HandleLevelEnd,
    //     60.0f,
    //     false
    // );

    // Initialize PlayerController
    PlayerController = UGameplayStatics::GetPlayerController(GetWorld(), 0);

    // create the UI
    ShooterUI = CreateWidget<UShooterUI>(UGameplayStatics::GetPlayerController(GetWorld(), 0), ShooterUIClass);
    ShooterUI->AddToViewport(0);
    ShooterUI->BP_ShowStartRoundButton();

    DisablePlayerInput();
    // StartRound();
}

AShooterGameMode::AShooterGameMode()
{
    PrimaryActorTick.bCanEverTick = true;
}

void AShooterGameMode::StartRound()
{
    if (bWaitingForRoundStart)
    {
        EnablePlayerInput();
        bWaitingForRoundStart = false;
        TimeRemaining = 60.0f; // Reset timer for the round
        GetWorld()->GetTimerManager().SetTimer(
        LevelEndTimerHandle,
        this,
        &AShooterGameMode::HandleLevelEnd,
        60.0f,
        false
        );

        if (ShooterUI)
        {
            ShooterUI->BP_HideStartRoundButton();
        }

        UE_LOG(LogTemp, Display, TEXT("Round %d started!"), CurrentRound);
    }
}

void AShooterGameMode::HandleLevelEnd()
{
    // Implement end-of-level logic here
    UE_LOG(LogTemp, Display, TEXT("Round %d ended!"), CurrentRound);

    if(CurrentRound < MaxRounds)
    {
        ++CurrentRound;
        bWaitingForRoundStart = true;
        //TimeRemaining = 60.0f; // Reset timer for next round

        if (ShooterUI)
        {
            ShooterUI->BP_ShowStartRoundButton();
        }
        UE_LOG(LogTemp, Display, TEXT("Waiting for player to start Round %d"), CurrentRound);

        DisablePlayerInput();

        // GetWorld()->GetTimerManager().SetTimer(
        //     LevelEndTimerHandle,
        //     this,
        //     &AShooterGameMode::HandleLevelEnd,
        //     60.0f,
        //     false
        // );

        // UE_LOG(LogTemp, Display, TEXT("Starting Round %d"), CurrentRound);
    }
    else
    {
        DisablePlayerInput();

        // Calculate and log accuracy
        CalculateAccuracy();

        // Calculate and log average spawn time
        CalculateAverageSpawnTime();
    }
	// Optionally show a Game Over widget
    // ShooterUI->ShowGameOver();
}

void AShooterGameMode::CalculateAccuracy()
{
    int32 TotalShots = SuccessfulHits + MissedShots;
    if (TotalShots > 0)
    {
        Accuracy = (static_cast<float>(SuccessfulHits) / static_cast<float>(TotalShots)) * 100.f;
    }
    else
    {
        Accuracy = 0.f;
    }

    UE_LOG(LogTemp, Display, TEXT("Successful shots: %d"), SuccessfulHits);
    UE_LOG(LogTemp, Display, TEXT("Missed shots: %d"), MissedShots);
    UE_LOG(LogTemp, Display, TEXT("Total shots: %d"), SuccessfulHits + MissedShots);
    UE_LOG(LogTemp, Display, TEXT("Player Accuracy: %.2f%%"), Accuracy);
}

void AShooterGameMode::CalculateAverageSpawnTime()
{
    if (TargetSpawnTimes.Num() > 0 && TargetShotTimes.Num() > 0)
    {
        float TotalTime = 0.f;

        for (int32 i = 0; i < SuccessfulHits; ++i)
        {
            TotalTime += (TargetShotTimes[i] - TargetSpawnTimes[i]);
        }

        float AvgTime = TotalTime / static_cast<float>(SuccessfulHits);
        UE_LOG(LogTemp, Display, TEXT("Total spawn time: %.2f"), TotalTime);
        UE_LOG(LogTemp, Display, TEXT("Average Reaction Time: %.2f seconds"), AvgTime);
    }
    else
    {
        UE_LOG(LogTemp, Display, TEXT("No targets were spawned or shot."));
    }
}

void AShooterGameMode::IncrementTeamScore(uint8 TeamByte)
{
	// retrieve the team score if any
	int32 Score = 0;
	if (int32* FoundScore = TeamScores.Find(TeamByte))
	{
		Score = *FoundScore;
	}

	// increment the score for the given team
	++Score;
	TeamScores.Add(TeamByte, Score);

	// update the UI
	ShooterUI->BP_UpdateScore(TeamByte, Score);
}

// Enable player input
void AShooterGameMode::EnablePlayerInput()
{
    if (PlayerController)
    {
        PlayerController->SetPause(false);
        PlayerController->bShowMouseCursor = false;
    }
}

// Disable player input
void AShooterGameMode::DisablePlayerInput()
{
    if (PlayerController)
    {
        PlayerController->SetPause(true);
        PlayerController->bShowMouseCursor = true;
    }
}

void AShooterGameMode::Tick(float DeltaSeconds)
{
    Super::Tick(DeltaSeconds);

    if (TimeRemaining > 0.f)
    {
        TimeRemaining -= DeltaSeconds;
        float SecondsLeft = FMath::Max(0.f, TimeRemaining);

        if(ShooterUI != nullptr)
        {
            ShooterUI->BP_UpdateTimer(SecondsLeft);
        }
    }
}
