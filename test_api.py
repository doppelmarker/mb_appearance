#!/usr/bin/env python3
"""
Simple test script for the FastAPI web service.

This script tests basic API functionality without requiring external dependencies.
"""

import sys
import asyncio
from pathlib import Path

# Add the appearance module to the path
sys.path.insert(0, str(Path(__file__).parent))

async def test_api_basic():
    """Test basic API functionality."""
    print("Testing FastAPI basic functionality...")
    
    try:
        # Import the app
        from appearance.api.app import app
        print("✓ Successfully imported FastAPI app")
        
        # Test that we can create the app
        assert app is not None
        print("✓ App instance created successfully")
        
        # Test app metadata
        assert app.title == "Mount & Blade Warband Face Editor API"
        assert app.version == "1.0.0"
        print("✓ App metadata is correct")
        
        # Test session storage
        from appearance.api.session import get_session_storage
        storage = get_session_storage()
        assert storage is not None
        print("✓ Session storage initialized")
        
        # Test session creation
        session_id = await storage.create_session()
        assert session_id is not None
        assert len(session_id) > 0
        print(f"✓ Session created: {session_id}")
        
        # Test session retrieval
        session = await storage.get_session(session_id)
        assert session is not None
        print("✓ Session retrieved successfully")
        
        # Test session info
        info = await storage.get_session_info(session_id)
        assert info is not None
        assert info['session_id'] == session_id
        print("✓ Session info retrieved")
        
        # Test face code validation
        from appearance.face_code import validate_face_code
        valid_code = "0x000000018000004136db79b6db6db6fb00000000000000000000000000000000"
        assert validate_face_code(valid_code) == True
        print("✓ Face code validation works")
        
        # Test cleanup
        success = await storage.delete_session(session_id)
        assert success == True
        print("✓ Session cleanup successful")
        
        print("\n🎉 All basic API tests passed!")
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

async def test_api_models():
    """Test Pydantic models."""
    print("\nTesting API models...")
    
    try:
        from appearance.api.models import (
            CharacterInfo, 
            FaceCodeComponents,
            SessionInfo
        )
        
        # Test CharacterInfo model
        char = CharacterInfo(
            index=0,
            name="TestChar",
            sex=0,
            skin=0,
            age=25,
            hairstyle=1,
            hair_color=5,
            banner=0,
            face_code="0x000000018000004136db79b6db6db6fb00000000000000000000000000000000"
        )
        assert char.name == "TestChar"
        print("✓ CharacterInfo model works")
        
        # Test FaceCodeComponents model
        components = FaceCodeComponents(
            morph_keys={"morph_key_0": 0, "morph_key_1": 1},
            hair=1,
            beard=0,
            skin=0,
            hair_texture=0,
            hair_color=5,
            age=25,
            skin_color=0
        )
        assert components.hair == 1
        print("✓ FaceCodeComponents model works")
        
        print("✓ All model tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Model test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_imports():
    """Test that all modules can be imported."""
    print("Testing module imports...")
    
    try:
        # Test core API imports
        from appearance.api import app, models, session, middleware
        print("✓ Core API modules imported")
        
        # Test endpoint imports
        from appearance.api import characters, face_codes, files
        print("✓ Endpoint modules imported")
        
        # Test that existing mb-app functionality still works
        from appearance import service, face_code, helpers, validators
        print("✓ Core mb-app modules imported")
        
        print("✓ All imports successful!")
        return True
        
    except Exception as e:
        print(f"❌ Import test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Run all tests."""
    print("=" * 60)
    print("FastAPI Web Service Test Suite")
    print("=" * 60)
    
    tests = [
        ("Module Imports", test_imports),
        ("API Models", test_api_models),
        ("Basic API Functionality", test_api_basic),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        print("-" * 40)
        
        if asyncio.iscoroutinefunction(test_func):
            result = await test_func()
        else:
            result = test_func()
            
        results.append((test_name, result))
    
    print("\n" + "=" * 60)
    print("TEST RESULTS:")
    print("=" * 60)
    
    all_passed = True
    for test_name, passed in results:
        status = "✓ PASS" if passed else "❌ FAIL"
        print(f"{test_name}: {status}")
        if not passed:
            all_passed = False
    
    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 ALL TESTS PASSED! FastAPI implementation is ready.")
        print("\nTo start the API server, run:")
        print("  python -m appearance.web_api")
        print("\nAPI Documentation will be available at:")
        print("  http://localhost:8000/docs")
    else:
        print("❌ SOME TESTS FAILED! Check the errors above.")
    print("=" * 60)
    
    return all_passed

if __name__ == "__main__":
    asyncio.run(main())