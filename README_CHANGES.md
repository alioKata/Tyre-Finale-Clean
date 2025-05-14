# Tyre-Finale Project Changes

## Overview of Changes

1. **Removed Email Verification**
   - Replaced database-based user authentication with file-based storage
   - User data is now stored in JSON files in the `data/users` directory
   - Each user has their own directory with a profile.json file and uploads folder

2. **Flash Cards Implementation**
   - Main page (`/main`) implements a carousel of flash cards with tire information
   - The last slide includes an upload button to analyze a tire image
   - After upload, redirects to results page

3. **Project Structure Cleanup**
   - Moved unnecessary files to the "Earaser" directory
   - Removed verification workflow
   - Simplified authentication flow

## File Structure

- `app/services/user_service.py` - New service for file-based user management
- `app/api/auth.py` - Updated auth API to use file-based storage
- `app/static/js/registration.js` - Redirects to main page instead of verification
- `app/static/js/main.js` - Updated to use file-based uploads
- `app/api/tire.py` - Updated to store user-specific tire uploads

## Deployment on Render

When deploying on Render:

1. Set up the PostgreSQL database (still needed for tire records)
2. Configure environment variables in the Render dashboard:
   - SECRET_KEY
   - DATABASE_URL
   - MODEL_PATH
   - CLASS_INDICES_PATH

3. Make sure the following directories exist and are writable:
   - `data/users`
   - `app/static/uploads`

## Next Steps

1. Test the application locally before deploying
2. Ensure all paths are correctly set up for file storage
3. Push to Git repository for deployment on Render 