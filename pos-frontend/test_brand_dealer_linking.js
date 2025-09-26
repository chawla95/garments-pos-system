#!/usr/bin/env node
/**
 * Test script for Brand-Dealer linking functionality
 * Run this to test the new many-to-many relationship
 */

const axios = require('axios');

const API_BASE = 'http://127.0.0.1:8000';

async function testBrandDealerLinking() {
  console.log('🧪 Testing Brand-Dealer Linking Functionality...');
  console.log('='.repeat(60));

  try {
    // Step 1: Create a dealer
    console.log('\n1. Creating a dealer...');
    const dealerResponse = await axios.post(`${API_BASE}/dealers/`, {
      name: 'Premium Fashion Supplier',
      gstin: 'GST987654321',
      contact: '+91-9876543210'
    });
    const dealer = dealerResponse.data;
    console.log(`✅ Dealer created: ${dealer.name} (ID: ${dealer.id})`);

    // Step 2: Create a brand
    console.log('\n2. Creating a brand...');
    const brandResponse = await axios.post(`${API_BASE}/brands/`, {
      name: 'Adidas'
    });
    const brand = brandResponse.data;
    console.log(`✅ Brand created: ${brand.name} (ID: ${brand.id})`);

    // Step 3: Link dealer to brand
    console.log('\n3. Linking dealer to brand...');
    const linkResponse = await axios.post(`${API_BASE}/brands/${brand.id}/dealers/${dealer.id}`);
    console.log(`✅ ${linkResponse.data.message}`);

    // Step 4: Get dealers for brand
    console.log('\n4. Getting dealers for brand...');
    const dealersForBrand = await axios.get(`${API_BASE}/brands/${brand.id}/dealers`);
    console.log(`✅ Found ${dealersForBrand.data.length} dealer(s) for brand ${brand.name}:`);
    dealersForBrand.data.forEach(dealer => {
      console.log(`   - ${dealer.name} (${dealer.gstin})`);
    });

    // Step 5: Get brands for dealer
    console.log('\n5. Getting brands for dealer...');
    const brandsForDealer = await axios.get(`${API_BASE}/dealers/${dealer.id}/brands`);
    console.log(`✅ Found ${brandsForDealer.data.length} brand(s) for dealer ${dealer.name}:`);
    brandsForDealer.data.forEach(brand => {
      console.log(`   - ${brand.name}`);
    });

    // Step 6: Create another dealer and link to same brand
    console.log('\n6. Creating another dealer and linking to same brand...');
    const dealer2Response = await axios.post(`${API_BASE}/dealers/`, {
      name: 'Sports Gear Ltd',
      gstin: 'GST111222333',
      contact: '+91-1112223333'
    });
    const dealer2 = dealer2Response.data;
    console.log(`✅ Second dealer created: ${dealer2.name} (ID: ${dealer2.id})`);

    await axios.post(`${API_BASE}/brands/${brand.id}/dealers/${dealer2.id}`);
    console.log(`✅ Second dealer linked to brand ${brand.name}`);

    // Step 7: Show final state
    console.log('\n7. Final state - dealers for brand:');
    const finalDealers = await axios.get(`${API_BASE}/brands/${brand.id}/dealers`);
    console.log(`✅ Brand "${brand.name}" now has ${finalDealers.data.length} dealer(s):`);
    finalDealers.data.forEach(dealer => {
      console.log(`   - ${dealer.name} (${dealer.gstin})`);
    });

    console.log('\n' + '='.repeat(60));
    console.log('🎉 Brand-Dealer linking test completed successfully!');
    console.log('📖 You can now test this in the UI at: http://localhost:3000');
    console.log('🔗 Go to Brands tab → Link Dealers to see the functionality');

  } catch (error) {
    console.error('❌ Test failed:', error.response?.data || error.message);
  }
}

// Run the test
testBrandDealerLinking(); 