// Fill out your copyright notice in the Description page of Project Settings.


#include "TargetSpawner.h"
#include "Components/BoxComponent.h"
#include "Components/StaticMeshComponent.h"
#include "ShootingTarget.h"

// Sets default values
ATargetSpawner::ATargetSpawner()
{
 	// Set this actor to call Tick() every frame.  You can turn this off to improve performance if you don't need it.
	PrimaryActorTick.bCanEverTick = true;

	RootComp = CreateDefaultSubobject<UBoxComponent>(TEXT("RootComp"));
	RootComponent = RootComp;

	SpawnAreaMesh = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("SpawnAreaMesh"));
	SpawnAreaMesh->SetupAttachment(RootComp);
}

// Called when the game starts or when spawned
void ATargetSpawner::BeginPlay()
{
	Super::BeginPlay();

	SpawnTarget();
}

void ATargetSpawner::SpawnTarget()
{
	if (!TargetClass) {
        UE_LOG(LogTemp, Warning, TEXT("TargetClass is not set on TargetSpawner!"));
        return;
    }

	// Get box extent and origin
	FVector Origin = RootComp->GetComponentLocation();
	FVector Extent = RootComp->GetScaledBoxExtent();

	// Generate random point within box
	FVector RandomOffset = FVector(
	FMath::FRandRange(-Extent.X, Extent.X),
	FMath::FRandRange(-Extent.Y, Extent.Y),
	FMath::FRandRange(-Extent.Z, Extent.Z)
	);

	FVector SpawnLocation = Origin + RandomOffset;
	FRotator SpawnRotation = FRotator::ZeroRotator;

	FActorSpawnParameters SpawnParams;
	SpawnParams.Owner = this;
	SpawnParams.SpawnCollisionHandlingOverride = ESpawnActorCollisionHandlingMethod::AlwaysSpawn;

	AShootingTarget* SpawnedTarget = GetWorld()->SpawnActor<AShootingTarget>(TargetClass, SpawnLocation, SpawnRotation, SpawnParams);

	if (!SpawnedTarget)
	{
		UE_LOG(LogTemp, Error, TEXT("Failed to spawn target!"));
		return;
	}
	UE_LOG(LogTemp, Display, TEXT("Target spawned at %s"), *SpawnLocation.ToString());

	// Bind to OnDestroyed to respawn
	//SpawnedTarget->OnDestroyed.AddDynamic(this, &ATargetSpawner::HandleTargetDestroyed);
	SpawnedTarget->OnDestroyed.AddDynamic(this, &ATargetSpawner::HandleTargetDestroyed);
}

void ATargetSpawner::HandleTargetDestroyed(AActor* DestroyedActor)
{
	UE_LOG(LogTemp, Display, TEXT("Target destroyed: %s"), *DestroyedActor->GetName());
	SpawnTarget();
}

// Called every frame
void ATargetSpawner::Tick(float DeltaTime)
{
	Super::Tick(DeltaTime);

}

