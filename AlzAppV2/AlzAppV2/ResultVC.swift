//
//  ResultVC.swift
//  AlzAppV2
//
//  Created by Wang on 2020/11/21.
//

import Foundation
import UIKit

class ResultVC: UIViewController{
    
    @IBOutlet weak var resultImage: UIImageView!
    @IBOutlet weak var nameLabel: UILabel!
    @IBOutlet weak var relationshipLabel: UILabel!
    var photoString :String! = ""
    var nameString = ""
    var relationshipString = ""
    
    override func viewDidLoad() {
        super.viewDidLoad()
        nameLabel.text = nameString
        relationshipLabel.text = relationshipString
        if photoString != ""{
            let loadedImage = base64toImage(img: photoString)!.resizeImage(targetSize: CGSize(width: 250, height: 257))
            resultImage.image = loadedImage
        }
    }
    func base64toImage(img: String) -> UIImage? {
        if (img == "") {
          return nil
        }
        let dataDecoded : Data = Data(base64Encoded: img, options: .ignoreUnknownCharacters)!
        let decodedimage = UIImage(data: dataDecoded)
        return decodedimage!
    }
    
}
