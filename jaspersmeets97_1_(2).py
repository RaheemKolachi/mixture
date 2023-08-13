# -*- coding: utf-8 -*-
"""jaspersmeets97 1 (2).ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1xl7xePPg_QkourufC9jU0AwzcsxYJuh8
"""

import numpy as np
import pandas as pd
import tensorflow as tf
from tensorflow.keras import layers
from tensorflow.keras.models import Model
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split

# Load your data and preprocess it
data = pd.read_csv("data.csv")
# Separate features and labels
features = data.iloc[:,1:-1]
labels = data.iloc[:,-1]


# One-hot encode labels
labels = pd.get_dummies(labels).values

# Split the data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(features, labels, test_size=0.2, random_state=42)

# Conditional GAN generator
# Conditional GAN generator
def build_generator(latent_dim, num_features, num_classes, hidden_units=128, dropout_rate=0.5):
    input_noise = layers.Input(shape=(latent_dim,))
    input_label = layers.Input(shape=(num_classes,))
    x = layers.Concatenate()([input_noise, input_label])
    x = layers.Dense(hidden_units, activation="relu")(x)
    x = layers.Dropout(dropout_rate)(x)
    x = layers.Dense(hidden_units, activation="relu")(x)
    x = layers.Dropout(dropout_rate)(x)
    x = layers.Dense(hidden_units, activation="relu")(x)
    x = layers.Dropout(dropout_rate)(x)
    output = layers.Dense(num_features, activation="sigmoid")(x)
    generator = Model(inputs=[input_noise, input_label], outputs=output)
    return generator

# Conditional GAN discriminator
def build_discriminator(num_features, num_classes, hidden_units=128, dropout_rate=0.5):
    input_feature = layers.Input(shape=(num_features,))
    input_label = layers.Input(shape=(num_classes,))
    x = layers.Concatenate()([input_feature, input_label])
    x = layers.Dense(hidden_units, activation="relu")(x)
    x = layers.Dropout(dropout_rate)(x)
    x = layers.Dense(hidden_units, activation="relu")(x)
    x = layers.Dropout(dropout_rate)(x)
    x = layers.Dense(hidden_units, activation="relu")(x)
    x = layers.Dropout(dropout_rate)(x)
    output = layers.Dense(1, activation="sigmoid")(x)
    discriminator = Model(inputs=[input_feature, input_label], outputs=output)
    return discriminator


# Create the GAN model
def build_gan(generator, discriminator, latent_dim, num_classes):
    input_noise = layers.Input(shape=(latent_dim,))
    input_label = layers.Input(shape=(num_classes,))
    generated_feature = generator([input_noise, input_label])
    discriminator.trainable = False
    validity = discriminator([generated_feature, input_label])
    gan = Model(inputs=[input_noise, input_label], outputs=validity)
    return gan

# Hyperparameters
latent_dim = 100
num_classes = y_train.shape[1]
num_features = X_train.shape[1]
hidden_units = 128
epochs = 10000
batch_size = 64

# Instantiate the models
generator = build_generator(latent_dim, num_features, num_classes, hidden_units)
discriminator = build_discriminator(num_features, num_classes, hidden_units)
gan = build_gan(generator, discriminator, latent_dim, num_classes)

# Compile the models
optimizer = tf.keras.optimizers.Adam(0.0002, 0.5)
discriminator.compile(optimizer=optimizer, loss="binary_crossentropy")
gan.compile(optimizer=optimizer, loss="binary_crossentropy")

# Train the models
real = np.ones((batch_size, 1))
fake = np.zeros((batch_size, 1))

for epoch in range(epochs):
    # Select a random batch of real samples
    idx = np.random.randint(0, X_train.shape[0], batch_size)
    real_features = X_train.iloc[idx].values
    real_labels = y_train[idx]

    # Generate a batch of fake samples
    noise = np.random.normal(0, 1, (batch_size, latent_dim))
    sampled_labels = np.eye(num_classes)[np.random.choice(num_classes, batch_size)]
    fake_features = generator.predict([noise, sampled_labels])

    # Train the discriminator
    d_loss_real = discriminator.train_on_batch([real_features, real_labels], real)
    d_loss_fake = discriminator.train_on_batch([fake_features, sampled_labels], fake)
    d_loss = 0.5 * np.add(d_loss_real, d_loss_fake)

    # Train the generator
    noise = np.random.normal(0, 1, (batch_size, latent_dim))
    sampled_labels = np.eye(num_classes)[np.random.choice(num_classes, batch_size)]
    g_loss = gan.train_on_batch([noise, sampled_labels], real)

    # Print progress
    if epoch % 1000 == 0:
        print(f"Epoch {epoch}/{epochs}, [D loss: {d_loss}] [G loss: {g_loss}]")


# Generate new samples
noise = np.random.normal(0, 1, (1, latent_dim))
sampled_label = np.eye(num_classes)[np.random.choice(num_classes, 1)]
generated_feature = generator.predict([noise, sampled_label])
print("Generated feature:", generated_feature)

# Generate 10 samples
num_samples = 10
noise = np.random.normal(0, 1, (num_samples, latent_dim))
sampled_labels = np.eye(num_classes)[np.random.choice(num_classes, num_samples)]
generated_samples = generator.predict([noise, sampled_labels])

# Print the generated samples
for i in range(num_samples):
    print(f"Generated sample {i + 1}: {generated_samples[i]}")
