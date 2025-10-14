// Fill out your copyright notice in the Description page of Project Settings.

#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "TargetSpawner.generated.h"

class AShootingTarget;
class UBoxComponent;
class UStaticMeshComponent;

UCLASS()
class SHOOTINGGROUNDS_API ATargetSpawner : public AActor
{
	GENERATED_BODY()

	// Root component for the spawner and spawn area
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Components", meta = (AllowPrivateAccess = "true"))
	UBoxComponent* RootComp;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Components", meta = (AllowPrivateAccess = "true"))
	UStaticMeshComponent* SpawnAreaMesh;

public:	
	// Sets default values for this actor's properties
	ATargetSpawner();

protected:
	// Called when the game starts or when spawned
	virtual void BeginPlay() override;

	virtual void SpawnTarget();

	UPROPERTY(EditAnywhere, Category="Spawning")
	TSubclassOf<AShootingTarget> TargetClass;

	UFUNCTION()
	void HandleTargetDestroyed(AActor* DestroyedActor);

public:	
	// Called every frame
	virtual void Tick(float DeltaTime) override;

};
