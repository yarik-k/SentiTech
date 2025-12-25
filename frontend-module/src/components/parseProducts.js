import data from './auto-complete.json';

// extracts all full product names from auto-complete file: "Apple" + "IPhone 15" = "Apple IPhone 15"

export const getAllProducts = () => {
  const brands = Object.values(data);
  let allProducts = [];

  brands.forEach((brand) => {
    brand.forEach((brandObj) => {
      const brandName = brandObj.brand;
      const brandedProducts = brandObj.products.map(product => `${brandName} ${product}`);

      allProducts = allProducts.concat(brandedProducts);
    });
  });

  return allProducts;
};