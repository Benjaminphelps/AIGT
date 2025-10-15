// Copyright Epic Games, Inc. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "Blueprint/UserWidget.h"
#include "ShooterUI.generated.h"

/**
 *  Simple scoreboard UI for a first person shooter game
 */
UCLASS(abstract)
class SHOOTINGGROUNDS_API UShooterUI : public UUserWidget
{
	GENERATED_BODY()
	
public:

	/** Allows Blueprint to update score sub-widgets */
	UFUNCTION(BlueprintImplementableEvent, Category="Shooter", meta = (DisplayName = "Update Score"))
	void BP_UpdateScore(uint8 TeamByte, int32 Score);

	/** Allows Blueprint to update timer */
	UFUNCTION(BlueprintImplementableEvent, Category="Shooter", meta = (DisplayName = "Update Timer"))
	void BP_UpdateTimer(float SecondsLeft);

	/** Allows Blueprint to reveal Start Button */
	UFUNCTION(BlueprintImplementableEvent, Category="Shooter", meta = (DisplayName = "Show Start Round Button"))
	void BP_ShowStartRoundButton();

	/** Allows Blueprint to hide Start Button */
	UFUNCTION(BlueprintImplementableEvent, Category="Shooter", meta = (DisplayName = "Hide Start Round Button"))
	void BP_HideStartRoundButton();
};
