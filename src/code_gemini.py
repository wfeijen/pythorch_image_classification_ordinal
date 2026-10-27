from pathlib import Path

import torch
from PIL import Image
from torch import nn, optim
from torch.utils.data import DataLoader, Dataset
from torchvision import models, transforms

BATCHSIZE = 32
DATA_DIR = Path("/home/willem/Data_neurale_netwerken/classificatie_arbitrair_onderscheid")
TRAIN = DATA_DIR / "Werkplaats"
VOORBEELD = DATA_DIR / "Werkplaats" / "4" / "__9905.jpg"


# --- 1. Dataset & Data Loading ---
class OrdinalImageDataset(Dataset):
    """
    Verwacht een mapstructuur per klasse, bijv.:
    dataset/
        ├── 1_low/
        ├── 2_medium/
        └── 3_high/
    Mapnamen worden alfabetisch gesorteerd en omgezet naar 0.0, 1.0, 2.0 etc.
    """

    def __init__(self, root_dir, transform=None):
        self.root_dir = Path(root_dir)
        self.transform = transform
        self.classes = sorted(self.root_dir.iterdir())
        self.image_paths = []
        self.labels = []

        for idx, class_name in enumerate(self.classes):
            class_dir = self.root_dir / class_name
            if class_dir.is_dir():
                for img_name in Path(class_dir).iterdir():
                    if img_name.is_file() and img_name.suffix.lower() in (".png", ".jpg", ".jpeg"):
                        self.image_paths.append(class_dir / img_name)  # noqa: PTH118
                        # Ordinale labels als floats (0.0, 1.0, 2.0, ...) voor MSE Loss
                        self.labels.append(float(idx))

    def __len__(self):
        return len(self.image_paths)

    def __getitem__(self, idx):
        img_path = self.image_paths[idx]
        image = Image.open(img_path).convert("RGB")
        label = self.labels[idx]

        if self.transform:
            image = self.transform(image)

        return image, torch.tensor(label, dtype=torch.float32)


# --- 2. Model Preperatie (Transfer Learning) ---
def get_ordinal_model(num_classes, model_name="resnet18"):
    if model_name == "resnet18":
        model = models.resnet18(weights=models.ResNet18_Weights.DEFAULT)
        # Vervang de classifier layer door 1 enkele output (regressie)
        in_features = model.fc.in_features
        model.fc = nn.Linear(in_features, 1)
    elif model_name == "efficientnet_b0":
        model = models.efficientnet_b0(weights=models.EfficientNet_B0_Weights.DEFAULT)
        in_features = model.classifier[1].in_features
        model.classifier[1] = nn.Linear(in_features, 1)
    else:
        raise ValueError("Model niet ondersteund in dit voorbeeld")

    return model


# --- 3. Training Loop ---
def train_model(model, dataloader, criterion, optimizer, num_epochs=10, device="cpu"):
    model.to(device)
    model.train()

    for epoch in range(num_epochs):
        print(f"Epoch {epoch + 1}/{num_epochs}")
        running_loss = 0.0
        for images, labels in dataloader:
            images = images.to(device)
            labels = labels.to(device)

            optimizer.zero_grad()

            # Predictie shape is [batch_size, 1], we maaken dit [batch_size]
            outputs = model(images).squeeze(-1)
            loss = criterion(outputs, labels)

            loss.backward()
            optimizer.step()
            # print(".", end="", flush=True)
            print(f"Batch Loss: {loss.item():.4f}")

            running_loss += loss.item() * images.size(0)

        epoch_loss = running_loss / len(dataloader.dataset)
        print(f"Epoch {epoch + 1}/{num_epochs} - Loss (MSE): {epoch_loss:.4f}")

    return model


# --- 4. Omzetten van Regressie Predictie naar Ordinale Klasse ---
def predict_ordinal_class(model, image_tensor, num_classes, device="cpu"):
    model.eval()
    with torch.no_grad():
        image_tensor = image_tensor.unsqueeze(0).to(device)
        raw_output = model(image_tensor).item()

        # Clip de waarde tussen 0 en max_class (bijv. 0 tot 8 bij 9 klassen) en rond af
        predicted_class = round(max(0, min(num_classes - 1, raw_output)))
        return predicted_class, raw_output


# --- Main Uitvoering ---
if __name__ == "__main__":
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Gebruikt device: {device}")

    # Transforms (standaard preprocessing voor ImageNet modellen)
    data_transforms = transforms.Compose(
        [
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
        ]
    )

    # Vul hier het pad naar je data map in
    print("dataset en dataloader")
    dataset = OrdinalImageDataset(root_dir=TRAIN, transform=data_transforms)
    dataloader = DataLoader(dataset, batch_size=BATCHSIZE, shuffle=True)

    num_classes = len(dataset.classes)
    print("inlezen model")
    model = get_ordinal_model(num_classes=num_classes, model_name="resnet18")
    criterion = nn.MSELoss()  # Dwingt ordinale afstand af
    optimizer = optim.Adam(model.parameters(), lr=1e-4)
    print("start trainen")

    trained_model = train_model(model, dataloader, criterion, optimizer, num_epochs=5, device=device)

    predict_image_path = VOORBEELD
    predict_image = Image.open(predict_image_path).convert("RGB")
    predict_image_tensor = data_transforms(predict_image)
    predicted_class, raw_output = predict_ordinal_class(
        trained_model,
        predict_image_tensor,
        num_classes=num_classes,
        device=device
    )
    print(f"Predicted class: {predicted_class}, Raw output (regression value): {raw_output:.4f}")
