import os
import pymysql
import pymysql.cursors
from flask import Flask, jsonify, request, render_template_string

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

app = Flask(__name__)

DB_HOST = os.environ.get('DB_HOST')
DB_USER = os.environ.get('DB_USER')
DB_PASSWORD = os.environ.get('DB_PASSWORD')
DB_NAME = os.environ.get('DB_NAME')
DB_PORT = int(os.environ.get('DB_PORT', 3306)) if os.environ.get('DB_PORT') else 3306

# Seed Products matching the EXACT Frontend Schema
FALLBACK_PRODUCTS = [
    # --- WOMEN COLLECTION ---
     {
                id: 1,
                name: "Aurelia 18k Solitaire Ring",
                collection: "women",
                category: "ring",
                price: 5400,
                rating: 4.9,
                reviews: 42,
                image: "https://www.ornatejewels.com/cdn/shop/files/RJR05041YG_3.jpg?v=1758004949&width=900",
                desc: "Handcrafted in 18k yellow gold vermeil over recycled sterling silver with a brilliant 1ct lab-grown solitaire diamond."
            },
            {
                id: 2,
                name: "Celeste Layered Serpent Necklace",
                collection: "women",
                category: "necklace",
                price: 8950,
                rating: 4.8,
                reviews: 31,
                image: "https://moncheri.in/cdn/shop/files/close-up-snake-pendant-green-eyes-cz-stones.webp?v=1774100893&width=1000",
                desc: "A luxurious dual-strand chain necklace featuring a delicate snake chain paired with an emerald-accented pendant."
            },
            {
                id: 3,
                name: "Elysia Huggie Hoop Earrings",
                collection: "women",
                category: "earring",
                price: 4800,
                rating: 4.7,
                reviews: 28,
                image: "https://encrypted-tbn1.gstatic.com/shopping?q=tbn:ANd9GcRCvm0Eio6Swgceq6I94FAWZ7TmjlxWS1zu1M0FIWAONklZwqEbmkaglvPCKGDidrIigwlK0y3bqx48eGEIW4avy2hvEuHRnA",
                desc: "Dainty pavé-set huggie hoops designed for 24/7 wear with secure click closures."
            },
            {
                id: 4,
                name: "Seraphina Tennis Bracelet",
                collection: "women",
                category: "bracelet",
                price: 9950,
                rating: 5.0,
                reviews: 56,
                image: "https://lorvelleco.com/cdn/shop/files/50.webp?v=1780434643&width=960",
                desc: "An exquisite tennis bracelet encrusted with brilliant hand-set cubic zirconia stones."
            },
            {
                id: 5,
                name: "Lyra Geometric Statement Ring",
                collection: "women",
                category: "ring",
                price: 6200,
                rating: 4.6,
                reviews: 19,
                image: "https://kymee.in/cdn/shop/files/KRW0039_1.jpg?v=1752053564&width=493",
                desc: "Architectural lines meet warm 18k gold vermeil for an everyday statement."
            },
            {
                id: 6,
                name: "Ophelia Pearl Drop Pendant",
                collection: "women",
                category: "necklace",
                price: 5900,
                rating: 4.9,
                reviews: 38,
                image: "https://pheeora.com.au/cdn/shop/files/baroque_pearl_silver_gold_necklace_1.jpg?v=1732170479&width=493",
                desc: "A lustrous freshwater baroque pearl suspended from a delicate gold vermeil chain."
            },
            {
                id: 7,
                name: "Vesta Drop Chandelier Earrings",
                collection: "women",
                category: "earring",
                price: 7500,
                rating: 4.8,
                reviews: 22,
                image: "https://cdn2.zohoecommerce.com/product-images/buy-vanamala-green-stone-earrings-online.png/3274882000000447418/600x600?storefront_domain=www.svetara.com&format=webp",
                desc: "Graceful cascading gemstone drops designed for evening galas and celebrations."
            },
            {
                id: 8,
                name: "Kiran Chunky Curb Bracelet",
                collection: "women",
                category: "bracelet",
                price: 8200,
                rating: 4.7,
                reviews: 15,
                image: "https://www.warrenjames.co.uk/_assets/images/products/images_grey/1000/VEBR011.jpg?v=2.6.0",
                desc: "Bold yet lightweight curb link bracelet crafted in recycled 925 silver with heavy gold plating."
            },
            {
                id: 9,
                name: "Thalia Stacking Band Trio",
                collection: "women",
                category: "ring",
                price: 6900,
                rating: 4.9,
                reviews: 44,
                image: "https://i.etsystatic.com/5335581/r/il/e49390/1107944157/il_1588xN.1107944157_niiz.jpg",
                desc: "A set of three interlockable rings in yellow, rose, and white gold finishes."
            },
            {
                id: 10,
                name: "Helena Coin Medallion Necklace",
                collection: "women",
                category: "necklace",
                price: 7800,
                rating: 4.8,
                reviews: 33,
                image: "https://templeofthesun.com.au/cdn/shop/files/temple-of-the-sun-palas-coin-necklace-gold-vermeil-1146881791.jpg?v=1755577931&width=1280",
                desc: "Inspired by ancient Hellenistic coins, embossed with intricate goddess motifs."
            },
            {
                id: 11,
                name: "Astra Starburst Studs",
                collection: "women",
                category: "earring",
                price: 3500,
                rating: 4.9,
                reviews: 50,
                image: "https://encrypted-tbn3.gstatic.com/shopping?q=tbn:ANd9GcTjKVPFejUD0-q_AfZve32afVjMIxTg6uZjXCUSzGIVVaLhkEEc9aFL_J1WjbcjJ9iDXY_7N01d05xl_DYdSj9Epg3Sv4-TRFfERxDWhhWnfI9lEc5T789OjQ",
                desc: "Celestial starburst studs featuring a central zirconia sparkle."
            },
            {
                id: 12,
                name: "Iris Cuff Bangle",
                collection: "women",
                category: "bracelet",
                price: 8800,
                rating: 4.7,
                reviews: 18,
                image: "https://lajoyeria.co/cdn/shop/files/B3624_1.jpg?v=1758809644&width=990",
                desc: "An open adjustable cuff bangle with polished gemstone ends."
            },
            {
                id: 13,
                name: "Nesta Emerald Cocktail Ring",
                collection: "women",
                category: "ring",
                price: 4800,
                rating: 4.9,
                reviews: 29,
                image: "https://shayn.in/cdn/shop/files/QA123001_1.webp?v=1757935668&width=1946",
                desc: "A stunning emerald-cut green spinel centerpiece framed in halo crystals."
            },
            {
                id: 14,
                name: "Selene Crescent Moon Choker",
                collection: "women",
                category: "necklace",
                price: 7200,
                rating: 4.8,
                reviews: 24,
                image: "https://kymee.in/cdn/shop/files/KNP0009.3263copy.webp?v=1755837133&width=493",
                desc: "A delicate crescent moon pendant adorned with micro pavé stones."
            },
            {
                id: 15,
                name: "Daphne Evil Eye Protection Bracelet",
                collection: "women",
                category: "bracelet",
                price: 5200,
                rating: 4.9,
                reviews: 61,
                image: "https://kymee.in/cdn/shop/files/KBC0052.511copy.webp?v=1755169150&width=493",
                desc: "Enamel evil eye talisman set in 18k gold vermeil chain."
            },

            // --- MEN COLLECTION (14 items) ---
            {
                id: 16,
                name: "Titanium & Gold Minimalist Band",
                collection: "men",
                category: "ring",
                price: 6500,
                rating: 4.8,
                reviews: 35,
                image: "https://newmanbands.com/wp-content/uploads/2021/03/masterly-titanium-ring-for-men-gold-finish-wedding-band-engagement-ring-for-guys.webp",
                desc: "Robust brushed titanium core encased in a sleek 18k yellow gold vermeil stripe."
            },
            {
                id: 17,
                name: "Onyx Signet Ring for Men",
                collection: "men",
                category: "ring",
                price: 8950,
                rating: 4.9,
                reviews: 40,
                image: "https://encrypted-tbn2.gstatic.com/shopping?q=tbn:ANd9GcQrKTJaL-qwlzYHbvqZJhfxFizfLQY7LdiLrFnaPr71YRLnhh16ruxtapEYVOLeERgZsnsv692qk6QyBLHagN9USb6cM5RCDQ",
                desc: "Classic square signet ring featuring a polished black onyx stone inlay."
            },
            {
                id: 18,
                name: "Sleek Curb Chain Necklace (Men)",
                collection: "men",
                category: "necklace",
                price: 9800,
                rating: 4.9,
                reviews: 52,
                image: "https://i.etsystatic.com/13878029/r/il/da299e/3290617275/il_1588xN.3290617275_dft4.jpg",
                desc: "Heavy 5mm curb chain crafted in recycled 925 silver with durable gold plating."
            },
            {
                id: 19,
                name: "Regal Gold Cufflinks",
                collection: "men",
                category: "traditional",
                price: 3200,
                rating: 4.7,
                reviews: 21,
                image: "https://tossido.in/cdn/shop/files/uptown-cufflinks-5149722_1000x.jpg?v=1759393745",
                desc: "Polished geometric gold cufflinks with secure bullet-back closures for formal suiting."
            },
            {
                id: 20,
                name: "Ares Geometric Gold Studs (Men)",
                collection: "men",
                category: "earring",
                price: 4200,
                rating: 4.8,
                reviews: 19,
                image: "https://encrypted-tbn0.gstatic.com/shopping?q=tbn:ANd9GcTpkIasLyabWjKYMrH03hhNRHikKQbpKMjw-QSwZme3C0_U4yDDF25tSoeYSLCpTiadKJOJJbGjtPYQrwzj1SfikMKYB7IpsGZ3CWD1cpe68D4l3pE0d1zYqg",
                desc: "Square matte gold stud earrings designed for modern men's ear piercings."
            },
            {
                id: 21,
                name: "Minimalist Huggie Hoop (Single Men's Piercing)",
                collection: "men",
                category: "piercing",
                price: 3500,
                rating: 4.9,
                reviews: 30,
                image: "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcT_rXQv2Yt55mo1jmU-_Y7u8enOf8dvWTjWZ3sgqvwFqw&s",
                desc: "Single-sided sleek black and gold huggie hoop for everyday piercing wear."
            },
            {
                id: 22,
                name: "Braided Leather & Gold Bracelet",
                collection: "men",
                category: "bracelet",
                price: 6800,
                rating: 4.7,
                reviews: 25,
                image: "https://jerone.com/images/product/14886-Spirit-Leather-Bracelet-Stainless-Steel-Gold-Serasar-1691137176-B006.webp?w=1200",
                desc: "Genuine supple black leather braided with an 18k gold magnetic clasp."
            },
            {
                id: 23,
                name: "Solstice Box Chain Necklace",
                collection: "men",
                category: "necklace",
                price: 8500,
                rating: 4.8,
                reviews: 27,
                image: "https://encrypted-tbn3.gstatic.com/shopping?q=tbn:ANd9GcSmVmQgOirLqeyWDLutnWod-3sfem2H2iCNg3Dfmy7fpYTBpZeOlToVdzeY3w0bbl5etRjAq7jRtAakPGWKzeIFbiRA9ChnW6ij7M6nx_FZAsPDgnmGlKUzxg",
                desc: "Crisp geometric box chain offering a sleek, modern drape."
            },
            {
                id: 24,
                name: "Matte Black & Gold Band",
                collection: "men",
                category: "ring",
                price: 5900,
                rating: 4.6,
                reviews: 18,
                image: "https://encrypted-tbn1.gstatic.com/shopping?q=tbn:ANd9GcROe17RgIh2MS_THSrPU-XpdO-1uHQR5WvJCK7YTTMx0J1AZA9LRW0LVLa56S6RZ9xTcwuXEPVUBNPbb2NAKgyTCWVgxJn2lp1espeO5BOZg8QSSR7UdRToSg",
                desc: "Matte black tungsten carbide band with a polished gold inner groove."
            },
            {
                id: 25,
                name: "Minimalist Ear Cuff (Men's Non-Piercing)",
                collection: "men",
                category: "piercing",
                price: 3200,
                rating: 4.8,
                reviews: 22,
                image: "https://www.luxez.store/cdn/shop/files/rose_gold_2_8da36d71-a5be-4c23-b342-71e76566c644.png?v=1782389860&width=990",
                desc: "Clip-on ear cuff in 18k rose gold vermeil for instant edge without piercing."
            },
            {
                id: 26,
                name: "Herculean Solid Silver Chain Bracelet",
                collection: "men",
                category: "bracelet",
                price: 7900,
                rating: 4.9,
                reviews: 31,
                image: "https://encrypted-tbn1.gstatic.com/shopping?q=tbn:ANd9GcR5C-nnwo5aFIeT-bF1_xl4UC06csaPtixPb097inxKMQyAAwaIhTSikowPK47yOu8tceYh2nS1qm_8SNUvgtm-yLxejmdF",
                desc: "Substantial chain bracelet in polished sterling silver."
            },
            {
                id: 27,
                name: "Vintage Coin Cufflinks",
                collection: "men",
                category: "traditional",
                price: 6800,
                rating: 4.7,
                reviews: 14,
                image: "https://encrypted-tbn0.gstatic.com/shopping?q=tbn:ANd9GcSAsvb4PVZMpmIjVzcy2qb0flbrhHI8KuBO6XGea2RulsbNLyR4q2j2_Z-mfzvG1GgUVLNWOiASmc-HdaHUkZZ0ENuBr2TfpCYb7CVBnlHSHCzh4HPGpq8e",
                desc: "Detailed antique coin motif cufflinks for weddings and formal events."
            },
            {
                id: 28,
                name: "Vertex Geometric Men's Ring",
                collection: "men",
                category: "ring",
                price: 7200,
                rating: 4.8,
                reviews: 20,
                image: "https://m.media-amazon.com/images/I/61jGtn31chL.jpg",
                desc: "Faceted geometric edges with brushed gold finish."
            },
            {
                id: 29,
                name: "Prism Men's Huggie Earrings",
                collection: "men",
                category: "earring",
                price: 4500,
                rating: 4.7,
                reviews: 16,
                image: "https://www.shanaysilver.in/image/cache/wp/gj/products/men/earrings/M-ER-28-B-1024x1024.webp",
                desc: "Sleek prismatic cut huggie hoops for men."
            },

            // --- WEDDING & GUESTS COLLECTION (15 items) ---
            {
                id: 30,
                name: "Royal Polki Sherwani Mala",
                collection: "wedding",
                category: "traditional",
                price: 9950,
                rating: 5.0,
                reviews: 64,
                image: "https://muchmore.co.in/cdn/shop/files/ML-131_3_copy.jpg?v=1771870625&width=352",
                desc: "An exquisite multi-strand ceremonial mala featuring uncut polki stones and emerald bead drops for groom and wedding attendees."
            },
            {
                id: 31,
                name: "Regal Gold & Emerald Sherwani Brooch",
                collection: "wedding",
                category: "traditional",
                price: 8500,
                rating: 4.9,
                reviews: 48,
                image: "https://encrypted-tbn2.gstatic.com/shopping?q=tbn:ANd9GcRW0Wji-uGdgNFgQgIjb2KGaOHYu7S9IY56oDfJRJdetAyNTup9rUytPAJV7Ud8xOd16aM92Zwm09pab80NVqtSE3C9xMI1",
                desc: "Ornate safa pin and brooch embellished with emerald crystals and pearl tassels."
            },
            {
                id: 32,
                name: "Traditional Kundan Maang Tikka",
                collection: "wedding",
                category: "traditional",
                price: 7200,
                rating: 4.9,
                reviews: 55,
                image: "https://encrypted-tbn1.gstatic.com/shopping?q=tbn:ANd9GcSTnOE4JPcqRrNu7CIjNYi3Vs8CWIFGpj5MG7ICApfBo1lLAokIoTNbKBcCPfQ7tY18CS3VBmD5EY52_fME4CUtVsEirOX_eg",
                desc: "Handcrafted kundan maang tikka with delicate pearl bead drops for intimate wedding ceremonies."
            },
            {
                id: 33,
                name: "Delicate Gold Mangalsutra with Solitaire",
                collection: "wedding",
                category: "traditional",
                price: 9400,
                rating: 5.0,
                reviews: 82,
                image: "https://encrypted-tbn3.gstatic.com/shopping?q=tbn:ANd9GcTFhJWXsCGpqIT6US_NYxRTmhLjduL696tmpZ_vNrx3Nq0Zu5w0nvb02l_uYv75lqm4DjzQKVA36cUKTHKGMqy_tJipXvCsLHnhYd_ImkH3sJQVGs-MGXK4NQ",
                desc: "Modern minimalist mangalsutra featuring traditional black beads paired with a brilliant lab-grown diamond solitaire pendant."
            },
            {
                id: 34,
                name: "Polki Nath (Bridal Nose Ring)",
                collection: "wedding",
                category: "traditional",
                price: 6800,
                rating: 4.8,
                reviews: 39,
                image: "https://encrypted-tbn0.gstatic.com/shopping?q=tbn:ANd9GcTIxE9c5ktTy3MIcAOtQI66W2T9J71GjTR13Ot2nDitPkoGPmofFzu1Xmwo-R3aAgSQnnBtNJVRnWNTvl7AWd7Gb22de3lnGkxs1aY0K-KUyvByVy_YHcLTkhk",
                desc: "Lightweight clip-on or piercing polki nath adorned with seed pearls for wedding guests and brides."
            },
            {
                id: 35,
                name: "Eternal Promise Matching Couple Bands",
                collection: "wedding",
                category: "ring",
                price: 9950,
                rating: 4.9,
                reviews: 70,
                image: "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRpXzPEgkdw-pjn74ROXB6pcZimSV1MqW6oWUTJn218hQ&s=10",
                desc: "Matching set of polished 18k gold vermeil wedding bands with comfort-fit interiors."
            },
            {
                id: 36,
                name: "Sangeet Choker & Earring Set",
                collection: "wedding",
                category: "traditional",
                price: 9900,
                rating: 4.9,
                reviews: 45,
                image: "https://www.krystaljewels.com/cdn/shop/files/Ruby_Drop_Kundan_Statement_Choker_Set_2.png?v=1778334194&width=832",
                desc: "A stunning matching choker necklace and jhumka earring set designed for wedding receptions."
            },
            {
                id: 37,
                name: "Maharaja Emerald Cufflinks & Kurta Buttons",
                collection: "wedding",
                category: "traditional",
                price: 8900,
                rating: 4.8,
                reviews: 29,
                image: "https://shinydabba.com/cdn/shop/files/866a74be-e42e-46ec-9866-4267e807729a.png?v=1784724537&width=750",
                desc: "Complete set of 1 cufflinks and 6 matching kurta buttons with green gemstone accents."
            },
            {
                id: 38,
                name: "Intimate Wedding Diamond Jhumkas",
                collection: "wedding",
                category: "earring",
                price: 8500,
                rating: 4.9,
                reviews: 38,
                image: "https://kinclimg7.bluestone.com/f_jpg,c_scale,w_828,q_80,b_rgb:f0f0f0/giproduct/BISG0414D13_YAA18DIG6XXXXXXXX_ABCD00-PICS-00004-1024-26236.png",
                desc: "Lightweight fusion jhumkas featuring baroque pearls and gold filigree."
            },
            {
                id: 39,
                name: "Bridal Crystal Hathphool (Hand Harness)",
                collection: "wedding",
                category: "bracelet",
                price: 8200,
                rating: 4.8,
                reviews: 26,
                image: "https://www.astriajewellery.com/cdn/shop/files/ChatGPT_Image_Jul_11_2026_01_46_21_PM.webp?v=1785401481&width=493",
                desc: "Delicate bracelet connected to a finger ring via a shimmering crystal chain."
            },
            {
                id: 40,
                name: "Royal Zirconia Wedding Band Set",
                collection: "wedding",
                category: "ring",
                price: 8900,
                rating: 4.9,
                reviews: 41,
                image: "https://i.etsystatic.com/59727380/r/il/56a4fb/7359509023/il_600x600.7359509023_ezmz.jpg",
                desc: "Interlocking bridal wrap ring set encrusted with sparkling micro-pavé stones."
            },
            {
                id: 41,
                name: "Mehendi Celebration Layered Rani Haar",
                collection: "wedding",
                category: "necklace",
                price: 9950,
                rating: 5.0,
                reviews: 58,
                image: "https://www.sneharateria.com/cdn/shop/files/Untitled-1copy_7da588a7-a886-41e7-ac69-311bd5093e28.jpg?v=1727695366&width=1200",
                desc: "An imperial long layered necklace designed to complement ethnic lehengas and sarees."
            },
            {
                id: 42,
                name: "Groom's Pearl & Emerald Safa Mala",
                collection: "wedding",
                category: "traditional",
                price: 8600,
                rating: 4.8,
                reviews: 33,
                image: "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSuRaWNZU_2SKQRTKs-rq7YDpFWozAGPUucjQC7xyIzkjbP4RuuUw-Qpfg&s=10",
                desc: "Exquisite multi-strand pearl safa mala with carved emerald accents."
            },
            {
                id: 43,
                name: "Minimalist Mangalsutra Bracelet",
                collection: "wedding",
                category: "bracelet",
                price: 5400,
                rating: 4.9,
                reviews: 65,
                image: "https://encrypted-tbn3.gstatic.com/shopping?q=tbn:ANd9GcSaRczJcOR6wbY2Dns19Zi6zuN3jPQFb6lkz24fqo6x2NKmzqJxi-KtqsPZkF6qFc2W2YwcfuYIgWME3mmbQyTk6u3m_mbn",
                desc: "A contemporary twist on the traditional mangalsutra worn around the wrist."
            },
            {
                id: 44,
                name: "Celebration Crystal Earrings",
                collection: "wedding",
                category: "earring",
                price: 7800,
                rating: 4.8,
                reviews: 29,
                image: "https://m.media-amazon.com/images/I/71GYMA8N84L._SY395_.jpg",
                desc: "Dazzling cluster earrings designed for wedding reception glamour."
            },

            // --- MINIMAL COLLECTION (< ₹7,000) (14 items) ---
            {
                id: 45,
                name: "Dainty Gold Anklet with Charms",
                collection: "minimal",
                category: "anklets",
                price: 4500,
                rating: 4.9,
                reviews: 48,
                image: "https://m.media-amazon.com/images/I/411T65p4IeL._SY625_.jpg",
                desc: "Featherlight 18k gold vermeil anklet featuring tiny dangling star and disc charms."
            },
            {
                id: 46,
                name: "Minimalist Snake Anklet",
                collection: "minimal",
                category: "anklets",
                price: 4950,
                rating: 4.8,
                reviews: 39,
                image: "https://whitehathi.com/cdn/shop/files/Snake_Chain_Anklet-2.jpg?v=1753444554&width=110",
                desc: "Fluid and sleek snake chain anklet that catches the light with every step."
            },
            {
                id: 47,
                name: "Single Piercing Gold Ear Cuff Set",
                collection: "minimal",
                category: "piercing",
                price: 3800,
                rating: 4.8,
                reviews: 32,
                image: "https://i.etsystatic.com/15350130/r/il/a0d901/7568056150/il_fullxfull.7568056150_p58c.jpg",
                desc: "Minimal stackable ear cuffs requiring no additional piercings."
            },
            {
                id: 48,
                name: "Micro Solitaire Dainty Necklace",
                collection: "minimal",
                category: "necklace",
                price: 5200,
                rating: 4.9,
                reviews: 74,
                image: "https://www.luxez.store/cdn/shop/files/il_1588xN.3189630702_m9m3.jpg?v=1760005324&width=990",
                desc: "A single floating diamond zirconia on an ultra-fine 16-inch gold vermeil chain."
            },
            {
                id: 49,
                name: "Everyday Stacking Plain Band",
                collection: "minimal",
                category: "ring",
                price: 2750,
                rating: 4.9,
                reviews: 92,
                image: "https://encrypted-tbn2.gstatic.com/shopping?q=tbn:ANd9GcRzOf9bsaiPfiALjLM0bcZF8h_OoeMdmp1BLfopunrOOdg233WkKm7DoFknMedF82Ri5DlaP28pNutnRol7zsGFHa3H8dEZng",
                desc: "The ultimate minimalist smooth domed band for effortless everyday stacking."
            },
            {
                id: 50,
                name: "Minimalist Bar Stud Earrings",
                collection: "minimal",
                category: "earring",
                price: 3400,
                rating: 4.8,
                reviews: 45,
                image: "https://www.luxez.store/cdn/shop/files/Dainty_Bar_Studs-4.webp?v=1760086548&width=990",
                desc: "Clean geometric bar studs in polished 18k gold vermeil."
            },
            {
                id: 51,
                name: "Dainty Paperclip Chain Bracelet",
                collection: "minimal",
                category: "bracelet",
                price: 5800,
                rating: 4.9,
                reviews: 51,
                image: "https://encrypted-tbn1.gstatic.com/shopping?q=tbn:ANd9GcR_sNKpGGpE5aWOR1AEaz7-GkIiHbv86-sD0w8T1zBulRvodrEspFr-1S9fGokjdCDC0D9y3VPxokBQFv4jDjz-Mv1D-M2K",
                desc: "Modern minimalist paperclip link bracelet designed for lightweight daily wear."
            },
            {
                id: 52,
                name: "Minimalist Beaded Rose Pendant Necklace",
                collection: "minimal",
                category: "necklace",
                price: 4900,
                rating: 4.8,
                reviews: 37,
                image: "https://images.unsplash.com/photo-1515562141207-7a88fb7ce338?auto=format&fit=crop&q=80&w=800",
                desc: "Timeless Pearl Strand Necklace with Embellished Silver Rose Centric Clasp."
            },
            {
                id: 53,
                name: "Minimalist Geo Triangle Ring",
                collection: "minimal",
                category: "ring",
                price: 4200,
                rating: 4.7,
                reviews: 28,
                image: "https://i.etsystatic.com/27039204/r/il/be4a1e/5354298965/il_1588xN.5354298965_c9k4.jpg",
                desc: "Clean geometric triangle ring with brushed gold finish."
            },
            {
                id: 54,
                name: "Minimalist Beaded Choker",
                collection: "minimal",
                category: "necklace",
                price: 6500,
                rating: 4.9,
                reviews: 33,
                image: "https://i.etsystatic.com/11516823/r/il/bc4428/2979564281/il_1588xN.2979564281_rem1.jpg",
                desc: "Tiny spaced 18k gold beads along a delicate chain."
            },
            {
                id: 55,
                name: "Sleek Minimalist Hoop Earrings",
                collection: "minimal",
                category: "earring",
                price: 4600,
                rating: 4.9,
                reviews: 60,
                image: "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQWoXWb1D4rCnTxMMu_n9hoGe8KqUl7vEn2ImASUpV8ErRvrK91",
                desc: "Seamless medium-sized hoop earrings for timeless elegance."
            },
            {
                id: 56,
                name: "Minimalist Infinity Bracelet",
                collection: "minimal",
                category: "bracelet",
                price: 5100,
                rating: 4.8,
                reviews: 42,
                image: "https://kymee.in/cdn/shop/files/KBC0047.837.jpg?v=1751444836&width=493",
                desc: "Delicate chain featuring a polished infinity symbol centerpiece."
            }
]

def get_db_connection():
    if not DB_HOST or not DB_USER:
        return None
    return pymysql.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        port=DB_PORT,
        cursorclass=pymysql.cursors.DictCursor,
        ssl={'ssl': {}},
        connect_timeout=5
    )

@app.route('/')
def index():
    try:
        with open('index.html', 'r', encoding='utf-8') as f:
            return render_template_string(f.read())
    except FileNotFoundError:
        return "Error: index.html file not found in current directory.", 404

@app.route('/api/products', methods=['GET'])
def get_products():
    collection = request.args.get('collection', 'all')
    category = request.args.get('category', 'all')
    search_query = request.args.get('q', '').lower().strip()

    conn = None
    try:
        conn = get_db_connection()
        if conn:
            with conn.cursor() as cursor:
                query = "SELECT id, name, collection, category, price, rating, reviews, image, desc FROM products WHERE 1=1"
                params = []

                if collection != 'all':
                    query += " AND collection = %s"
                    params.append(collection)
                if category != 'all':
                    query += " AND category = %s"
                    params.append(category)
                if search_query:
                    query += " AND (LOWER(name) LIKE %s OR LOWER(desc) LIKE %s)"
                    params.extend([f"%{search_query}%", f"%{search_query}%"])

                cursor.execute(query, params)
                products = cursor.fetchall()
                conn.close()
                if products:
                    return jsonify(products)
    except Exception as e:
        app.logger.warning(f"Database query failed, serving fallback data. Error: {e}")
        if conn:
            try:
                conn.close()
            except:
                pass

    # Fallback in-memory filter matching frontend rules
    filtered = FALLBACK_PRODUCTS
    if collection != 'all':
        filtered = [p for p in filtered if p.get('collection') == collection]
    if category != 'all':
        filtered = [p for p in filtered if p.get('category') == category]
    if search_query:
        filtered = [p for p in filtered if search_query in p.get('name', '').lower() or search_query in p.get('desc', '').lower()]

    return jsonify(filtered)

@app.errorhandler(500)
def handle_500(e):
    return jsonify({"status": "error", "message": "Internal Server Error", "details": str(e)}), 500

        # Place the new authentication routes HERE (Above errorhandlers and main block)

@app.route('/api/auth/login', methods=['POST'])
def api_login():
    data = request.get_json() or {}
    email = data.get('email')
    password = data.get('password')
    if not email or not password:
        return jsonify({"status": "error", "message": "Email and password are required"}), 400
    
    return jsonify({
        "status": "success",
        "user": {
            "name": email.split('@')[0].capitalize(),
            "email": email
        }
    })

@app.route('/api/auth/forgot-password', methods=['POST'])
def api_forgot_password():
    data = request.get_json() or {}
    email = data.get('email')
    if not email:
        return jsonify({"status": "error", "message": "Email is required"}), 400
    
    return jsonify({
        "status": "success",
        "message": f"Password reset instructions sent to {email}"
    })


# ----------------------------------------------------
# EXISTING BOTTOM LINES IN YOUR app.py FILE:
# ----------------------------------------------------
@app.errorhandler(500)
def handle_500(e):
    return jsonify({"status": "error", "message": "Internal Server Error", "details": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
