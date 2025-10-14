// Copyright Epic Games, Inc. All Rights Reserved.


#include "Variant_Shooter/ShooterGameMode.h"
#include "ShooterUI.h"
#include "Kismet/GameplayStatics.h"
#include "Engine/World.h"

void AShooterGameMode::BeginPlay()
{
	Super::BeginPlay();

	// create the UI
	ShooterUI = CreateWidget<UShooterUI>(UGameplayStatics::GetPlayerController(GetWorld(), 0), ShooterUIClass);
	ShooterUI->AddToViewport(0);

	// Set timer to end level in 60 seconds
    GetWorld()->GetTimerManager().SetTimer(
        LevelEndTimerHandle,
        this,
        &AShooterGameMode::HandleLevelEnd,
        60.0f,
        false
    );
}

void AShooterGameMode::HandleLevelEnd()
{
    // Implement your end-of-level logic here
    UE_LOG(LogTemp, Display, TEXT("Level ended after one minute!"));

	// Optionally show a Game Over widget
    // ShooterUI->ShowGameOver();

    // Disable player input
    APlayerController* PC = UGameplayStatics::GetPlayerController(GetWorld(), 0);
    if (PC)
    {
        PC->SetPause(true);
        PC->bShowMouseCursor = true;
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

void AShooterGameMode::Tick(float DeltaSeconds)
{
    Super::Tick(DeltaSeconds);

    if (TimeRemaining > 0.f)
    {
        TimeRemaining -= DeltaSeconds;
        int32 SecondsLeft = FMath::Max(0, FMath::FloorToInt(TimeRemaining));
        ShooterUI->BP_UpdateTimer(SecondsLeft);
    }
}
