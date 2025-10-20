# Yandex Maps Integration

This project includes an interactive Yandex Maps widget for selecting coordinates when adding places, with a manual fallback option for when the map service is unavailable.

## Setup

1. **Get a Yandex Maps API Key** (Optional but recommended):
   - Visit [Yandex Developer Console](https://developer.tech.yandex.ru/)
   - Create a new project and get your API key
   - Make sure to enable the Maps API for your key

2. **Configure Environment Variables**:
   ```bash
   # Copy the example environment file
   cp admin-frontend/.env.example admin-frontend/.env
   
   # Edit the .env file and add your API key (optional)
   VITE_YANDEX_MAPS_API_KEY=your-actual-api-key-here
   ```

3. **Start the Development Server**:
   ```bash
   cd admin-frontend
   npm run dev
   ```

## Features

### Map Mode (when API key is configured and service is available)
- **Interactive Map**: Click anywhere on the map to select coordinates
- **Draggable Marker**: Drag the marker to fine-tune the location
- **Current Location**: Use the "Use Current Location" button to get your current coordinates
- **Manual Override**: You can still manually enter coordinates in the fields below the map
- **Real-time Updates**: Coordinates update automatically as you interact with the map

### Manual Mode (fallback when map is unavailable)
- **Manual Input Fields**: Clean interface for entering latitude and longitude directly
- **Precision Control**: Supports up to 6 decimal places for accurate coordinates
- **Automatic Fallback**: Switches to manual mode if API key is missing or service is down

### Smart Mode Switching
- **Toggle Switch**: Switch between Map Mode and Manual Mode
- **Error Handling**: Automatically detects API failures and suggests manual input
- **Seamless Transition**: Coordinates are preserved when switching between modes

## Usage

When adding a new place in the admin interface:

1. Click "Add place" button
2. Fill in the name and description
3. **Choose your coordinate input method**:

   **Option A - Map Mode (if available):**
   - Use the interactive map to select location
   - Click on the map to place the marker
   - Drag the marker to adjust the position
   - Use "Use Current Location" for your current position
   - Or manually enter coordinates in the fields below the map

   **Option B - Manual Mode:**
   - Toggle to manual mode using the switch
   - Enter latitude and longitude directly in the input fields
   - Use decimal degrees format (e.g., 55.7558, 37.6176)

4. The latitude and longitude will be automatically set
5. Save the place

## Fallback Scenarios

The component automatically handles these situations:

- **No API Key**: Shows manual input mode with a helpful message
- **API Service Down**: Displays error message and switches to manual mode
- **Network Issues**: Gracefully falls back to manual input
- **Invalid API Key**: Shows warning and enables manual mode

## API Compatibility

The map widget maintains full compatibility with the existing backend API:
- Sends `latitude` and `longitude` fields exactly as before
- No changes required to the backend
- Works with existing place creation endpoints
- Functions identically whether using map or manual input

## Troubleshooting

- **Map not loading**: The component will automatically switch to manual mode
- **API key errors**: Check that your API key is correctly set in the `.env` file, or use manual mode
- **Coordinates not updating**: Make sure the form fields are properly connected to the map component
- **Service unavailable**: Use the manual input mode - it works without any external dependencies
